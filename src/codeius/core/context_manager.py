"""
Context Management System for Codeius AI Coding Agent
Handles project context, state tracking, and semantic code search
"""
import os
import json
import pickle
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import ast
import re
from codeius.core.performance import FileOperationCache, generate_cache_key
from codeius.utils.logger import agent_logger


@dataclass
class CodeContext:
    """Represents context for a specific code element"""
    name: str
    file_path: str
    content: str
    line_start: int
    line_end: int
    context_type: str  # 'function', 'class', 'variable', 'import', etc.
    dependencies: List[str] = field(default_factory=list)  # paths to dependencies
    references: List[str] = field(default_factory=list)  # paths to references


@dataclass
class ProjectContext:
    """Represents project-wide context information"""
    project_name: str
    root_path: str
    last_accessed: datetime
    files: List[str] = field(default_factory=list)
    file_mtimes: Dict[str, float] = field(default_factory=dict)
    imports: Dict[str, List[str]] = field(default_factory=dict)  # file -> imported modules
    functions: List[CodeContext] = field(default_factory=list)
    classes: List[CodeContext] = field(default_factory=list)
    variables: List[CodeContext] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    recent_files: List[str] = field(default_factory=list)


class ContextManager:
    """Manages project context and state across sessions"""
    
    def __init__(self, context_dir: str = ".codeius_context"):
        self.context_dir = Path(context_dir)
        self.current_project: Optional[ProjectContext] = None
        self.context_file = self.context_dir / "context.json"
        self.state_file = self.context_dir / "state.pkl"
        self.file_analysis_cache = FileOperationCache(ttl_seconds=3600) # Cache file analysis for 1 hour
        
        # Ensure context directory exists
        self.context_dir.mkdir(exist_ok=True)
        
        # Load existing context if available
        self.load_context()
    
    def load_context(self) -> bool:
        """Load project context from file"""
        try:
            if self.context_file.exists():
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Reconstruct ProjectContext
                self.current_project = ProjectContext(
                    project_name=data['project_name'],
                    root_path=data['root_path'],
                    last_accessed=datetime.fromisoformat(data['last_accessed']),
                    files=data['files'],
                    file_mtimes=data.get('file_mtimes', {}),
                    imports=data.get('imports', {}),
                    dependencies=data.get('dependencies', []),
                    recent_files=data.get('recent_files', [])
                )
                return True
        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            agent_logger.app_logger.warning(f"Error loading project context from {self.context_file}: {e}. Starting fresh.")
            # Consider using handle_error here if context loading failure is a critical, reportable error
            # For now, we log and return False to indicate reinitialization
            return False
        
        return False
    
    def save_context(self):
        """Save project context to file"""
        if not self.current_project:
            return
            
        data = {
            'project_name': self.current_project.project_name,
            'root_path': self.current_project.root_path,
            'last_accessed': self.current_project.last_accessed.isoformat(),
            'files': self.current_project.files,
            'file_mtimes': self.current_project.file_mtimes,
            'imports': self.current_project.imports,
            'dependencies': self.current_project.dependencies,
            'recent_files': self.current_project.recent_files[-20:]  # Keep last 20
        }
        
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    
    def set_project(self, project_path: str, project_name: Optional[str] = None):
        """Set the current project context"""
        if not os.path.exists(project_path):
            raise ValueError(f"Project path does not exist: {project_path}")
        
        abs_path = os.path.abspath(project_path)
        name = project_name or os.path.basename(abs_path)
        
        self.current_project = ProjectContext(
            project_name=name,
            root_path=abs_path,
            last_accessed=datetime.now(),
            recent_files=[],
            imports={},
            dependencies=[]
        )
        
        # Analyze project structure
        self.analyze_project_structure()
        self.save_context()
    
    def analyze_project_structure(self):
        """Analyze project structure and populate context"""
        if not self.current_project:
            return
        
        root_path = Path(self.current_project.root_path)
        
        # Find all Python files in the project
        py_files = list(root_path.rglob("*.py"))
        self.current_project.files = [str(f.relative_to(root_path)) for f in py_files]
        
        # Analyze each Python file for functions, classes, imports, etc.
        updated_mtimes = {}
        for py_file in py_files:
            rel_path = str(py_file.relative_to(root_path))
            current_mtime = py_file.stat().st_mtime

            if rel_path not in self.current_project.file_mtimes or \
               self.current_project.file_mtimes[rel_path] < current_mtime:
                try:
                    self.analyze_file(py_file)
                    updated_mtimes[rel_path] = current_mtime
                except Exception as e:
                    agent_logger.app_logger.warning(f"Skipping file {py_file} due to analysis error: {e}")
                    continue
            else:
                # File has not changed, retain old mtime
                updated_mtimes[rel_path] = self.current_project.file_mtimes[rel_path]

        self.current_project.file_mtimes = updated_mtimes

    
    def analyze_file(self, file_path: Path):
        """Analyze a single file and extract code elements"""
        if not self.current_project:
            return
        
        try:
            rel_path = str(file_path.relative_to(Path(self.current_project.root_path)))
            # Remove old entries for this file before re-analyzing
            self.current_project.functions = [f for f in self.current_project.functions if f.file_path != rel_path]
            self.current_project.classes = [c for c in self.current_project.classes if c.file_path != rel_path]
            self.current_project.imports.pop(rel_path, None)

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            cache_key = generate_cache_key(rel_path, hashlib.md5(content.encode()).hexdigest())
            cached_analysis = self.file_analysis_cache.get(cache_key, str(file_path))

            if cached_analysis:
                self.current_project.imports[rel_path] = cached_analysis["imports"]
                self.current_project.functions.extend(cached_analysis["functions"])
                self.current_project.classes.extend(cached_analysis["classes"])
                return

            # Track this file as recently accessed
            rel_path = str(file_path.relative_to(Path(self.current_project.root_path)))
            if rel_path not in self.current_project.recent_files:
                self.current_project.recent_files.append(rel_path)
            
            # Parse the file with AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                # Skip files with syntax errors
                return
            
            # Extract imports
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            # Store imports for this file
            rel_path = str(file_path.relative_to(Path(self.current_project.root_path)))
            self.current_project.imports[rel_path] = imports
            
            # Extract functions, classes, and variables
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    context = CodeContext(
                        name=node.name,
                        file_path=rel_path,
                        content=content.split('\n')[node.lineno-1:node.end_lineno],
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        context_type='function'
                    )
                    self.current_project.functions.append(context)
                
                elif isinstance(node, ast.ClassDef):
                    context = CodeContext(
                        name=node.name,
                        file_path=rel_path,
                        content=content.split('\n')[node.lineno-1:node.end_lineno],
                        line_start=node.lineno,
                        line_end=node.end_lineno,
                        context_type='class'
                    )
                    self.current_project.classes.append(context)

            # Cache the extracted analysis
            self.file_analysis_cache.set(cache_key, str(file_path), {
                "imports": self.current_project.imports.get(rel_path, []),
                "functions": [f for f in self.current_project.functions if f.file_path == rel_path],
                "classes": [c for c in self.current_project.classes if c.file_path == rel_path],
            })

        except Exception as e:
            agent_logger.app_logger.warning(f"Error processing file {rel_path} for context extraction: {e}")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current project context"""
        if not self.current_project:
            return {"error": "No project context set"}
        
        return {
            'project_name': self.current_project.project_name,
            'root_path': self.current_project.root_path,
            'files_count': len(self.current_project.files),
            'functions_count': len(self.current_project.functions),
            'classes_count': len(self.current_project.classes),
            'recent_files': self.current_project.recent_files[-5:],
            'dependencies': self.current_project.dependencies[:10],  # First 10
            'last_accessed': self.current_project.last_accessed.isoformat()
        }
    
    def find_function(self, function_name: str) -> Optional[CodeContext]:
        """Find a function by name"""
        if not self.current_project:
            return None
        
        for func in self.current_project.functions:
            if func.name == function_name:
                return func
        
        # Also look for functions with similar names
        for func in self.current_project.functions:
            if function_name.lower() in func.name.lower():
                return func
        
        return None
    
    def find_class(self, class_name: str) -> Optional[CodeContext]:
        """Find a class by name"""
        if not self.current_project:
            return None
        
        for cls in self.current_project.classes:
            if cls.name == class_name:
                return cls
        
        # Also look for classes with similar names
        for cls in self.current_project.classes:
            if class_name.lower() in cls.name.lower():
                return cls
        
        return None
    
    def semantic_search(self, query: str) -> List[CodeContext]:
        """Perform semantic search across the codebase"""
        if not self.current_project:
            return []
        
        results = []
        query_lower = query.lower()
        
        # Search in functions
        for func in self.current_project.functions:
            if (query_lower in func.name.lower() or 
                any(query_lower in line.lower() for line in func.content)):
                results.append(func)
        
        # Search in classes
        for cls in self.current_project.classes:
            if (query_lower in cls.name.lower() or 
                any(query_lower in line.lower() for line in cls.content)):
                results.append(cls)
        
        # Sort by relevance (exact matches first)
        results.sort(key=lambda x: (
            query_lower == x.name.lower(),  # Exact matches first
            query_lower in x.name.lower(),  # Partial name matches next
            len([line for line in x.content if query_lower in line.lower()])  # More matches first
        ), reverse=True)
        
        return results[:10]  # Return top 10 results
    
    def get_file_context(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get context information for a specific file"""
        if not self.current_project:
            return None
        
        # Find functions and classes in the file
        file_functions = [f for f in self.current_project.functions if f.file_path == file_path]
        file_classes = [c for c in self.current_project.classes if c.file_path == file_path]
        
        return {
            'file_path': file_path,
            'functions': [f.name for f in file_functions],
            'classes': [c.name for c in file_classes],
            'imports': self.current_project.imports.get(file_path, []),
            'related_files': self.get_related_files(file_path)
        }
    
    def get_related_files(self, file_path: str) -> List[str]:
        """Get files that are related to the given file based on imports/usage"""
        if not self.current_project:
            return []
        
        # This is a simple implementation; in a full implementation, 
        # you'd have more sophisticated relationship tracking
        related = set()
        
        # Find files that import this file
        for f_path, imports in self.current_project.imports.items():
            for imp in imports:
                # If the file is imported by this file, they're related
                if file_path.replace('.py', '').replace('/', '.') in imp or \
                   file_path.replace('.py', '').replace('\\', '.') in imp:
                    related.add(f_path)
        
        return list(related)
    
    def update_file_context(self, file_path: str):
        """Update context for a specific file (when it's modified)"""
        if not self.current_project:
            return
        
        # Remove old entries for this file
        self.current_project.functions = [f for f in self.current_project.functions if f.file_path != file_path]
        self.current_project.classes = [c for c in self.current_project.classes if c.file_path != file_path]
        
        # Re-analyze the file
        abs_file_path = Path(self.current_project.root_path) / file_path
        if abs_file_path.exists():
            self.analyze_file(abs_file_path)
        
        # Update context file
        self.save_context()
    
    def get_project_dependencies(self) -> List[str]:
        """Analyze and return project dependencies"""
        if not self.current_project:
            return []
        
        all_imports = set()
        for imports_list in self.current_project.imports.values():
            all_imports.update(imports_list)
        
        # Filter to only top-level imports (not submodules)
        top_level_imports = set()
        for imp in all_imports:
            parts = imp.split('.')
            if len(parts) > 0:
                top_level_imports.add(parts[0])
        
        # Remove built-in modules to get external dependencies
        import sys
        builtin_modules = set(sys.builtin_module_names)
        builtin_modules.update(['os', 'sys', 'json', 'pathlib', 'datetime', 'typing', 'dataclasses'])
        
        external_deps = [imp for imp in top_level_imports if imp not in builtin_modules]
        return sorted(list(external_deps))