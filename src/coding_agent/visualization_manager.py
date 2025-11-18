"""
Visualization Management System for Codeius AI Coding Agent

This module handles all visualization features including dependency graphs, 
project structure visualization, and performance metrics dashboards.
"""
import os
import sys
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
import networkx as nx
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from dataclasses import dataclass, field
from datetime import datetime
import subprocess


@dataclass
class VisualizationConfig:
    """Configuration settings for visualizations."""
    # Output settings
    output_dir: str = "visualizations"
    file_format: str = "png"  # png, svg, pdf
    dpi: int = 300
    
    # Graph settings
    graph_layout: str = "spring"  # spring, circular, random, etc.
    node_size: int = 300
    font_size: int = 8
    font_weight: str = "bold"
    
    # Color settings
    color_scheme: str = "default"  # default, dark, light
    dependency_edge_color: str = "#3498db"  # blue
    file_node_color: str = "#2ecc71"  # green
    class_node_color: str = "#e74c3c"  # red
    function_node_color: str = "#f39c12"  # orange


class VisualizationManager:
    """Manages all visualization features for the Codeius agent."""
    
    def __init__(self, workspace_root: str = "."):
        self.workspace_root = Path(workspace_root).resolve()
        self.config = VisualizationConfig()
        self.output_path = self.workspace_root / self.config.output_dir
        self.output_path.mkdir(exist_ok=True)
        
        # Initialize matplotlib to ensure it works in the current environment
        self._init_matplotlib()
    
    def _init_matplotlib(self):
        """Initialize matplotlib backend for compatibility."""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
        except ImportError:
            print("Warning: matplotlib not available. Visualization features will be limited.")
    
    def generate_dependency_graph(self, project_path: Optional[str] = None) -> str:
        """Generate a code dependency graph for the project."""
        if project_path is None:
            project_path = str(self.workspace_root)
        
        # Build dependency graph
        graph = self._build_dependency_graph(project_path)
        
        if not graph.nodes():
            return "No dependencies found in the project."
        
        # Create visualization
        output_file = self.output_path / f"dependency_graph_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{self.config.file_format}"
        self._visualize_dependency_graph(graph, str(output_file))
        
        return f"Dependency graph saved to: {output_file}"
    
    def _build_dependency_graph(self, project_path: str) -> nx.DiGraph:
        """Build a dependency graph from the project files."""
        graph = nx.DiGraph()
        
        project_root = Path(project_path)
        
        # Find all Python files in the project
        python_files = list(project_root.rglob("*.py"))
        
        # Add all Python files as nodes
        for file_path in python_files:
            relative_path = file_path.relative_to(project_root)
            node_id = str(relative_path)
            graph.add_node(node_id, type='file', path=str(file_path))
        
        # Analyze dependencies between files
        for file_path in python_files:
            relative_path = file_path.relative_to(project_root)
            imports = self._extract_imports(file_path)
            
            for imported_module in imports:
                # Try to find the corresponding file for the import
                imported_file = self._resolve_import_to_file(imported_module, file_path, project_root)
                if imported_file and imported_file.exists():
                    imported_relative = imported_file.relative_to(project_root)
                    if str(imported_relative) in graph.nodes:
                        # Add directed edge from the current file to the imported file
                        graph.add_edge(str(relative_path), str(imported_relative))
        
        return graph
    
    def _extract_imports(self, file_path: Path) -> List[str]:
        """Extract import statements from a Python file."""
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple parsing to extract import statements
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                
                # Handle 'import module'
                if line.startswith('import '):
                    module = line[7:].split(',')[0].strip().split('.')[0]  # Take first module if multiple imports
                    imports.add(module)
                
                # Handle 'from module import something'
                elif line.startswith('from '):
                    parts = line.split(' import ')
                    if len(parts) >= 2:
                        module = parts[0][5:].strip()  # Remove 'from ' prefix
                        imports.add(module)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        # Filter out common Python built-in modules
        filtered_imports = []
        for imp in imports:
            # Remove leading dots for relative imports
            clean_imp = imp.lstrip('.').split('.')[0]
            if clean_imp and clean_imp not in ['os', 'sys', 'json', 'pathlib', 'typing', 'datetime', 'subprocess', 
                                              're', 'collections', 'itertools', 'functools', 'operator', 'math',
                                              'random', 'time', 'logging', 'argparse', 'configparser', 'urllib',
                                              'http', 'email', 'calendar', 'gzip', 'zipfile', 'tarfile', 'shutil',
                                              'threading', 'multiprocessing', 'asyncio', 'concurrent', 'queue',
                                              'heapq', 'bisect', 'array', 'struct', 'hashlib', 'hmac', 'base64',
                                              'binascii', 'codecs', 'string', 'textwrap', 're', 'sre', 'sre_parse',
                                              'sre_constants', 'copy', 'pprint', 'reprlib', 'enum', 'types', 'typing',
                                              'abc', 'atexit', 'contextlib', 'copyreg', 'enum', 'formatter', 'functools',
                                              'importlib', 'inspect', 'keyword', 'operator', 'token', 'tokenize',
                                              'traceback', 'trace', 'warnings', 'weakref', 'abc', 'asyncio', 'collections',
                                              'copy', 'dataclasses', 'functools', 'heapq', 'itertools', 'operator',
                                              'os', 'pathlib', 're', 'types', 'typing', 'unittest']:
                filtered_imports.append(imp)
        
        return filtered_imports
    
    def _resolve_import_to_file(self, import_module: str, current_file: Path, project_root: Path) -> Optional[Path]:
        """Resolve an import to a file path."""
        # Handle relative imports (starting with .)
        if import_module.startswith('.'):
            # Relative import - compute from current file location
            current_dir = current_file.parent
            
            # Count leading dots to determine how many levels up to go
            dot_count = 0
            for char in import_module:
                if char == '.':
                    dot_count += 1
                else:
                    break
            
            # Remove leading dots from module name
            module_name = import_module[dot_count:]
            
            # Go up 'dot_count - 1' levels from current directory
            base_path = current_dir
            for _ in range(dot_count - 1):
                base_path = base_path.parent
            
            # Now construct the path based on the module name
            module_path = base_path / module_name.replace('.', os.sep)
            
            # Check if this path is a directory with an __init__.py
            if module_path.is_dir():
                init_file = module_path / "__init__.py"
                if init_file.exists():
                    return init_file
            
            # Or try as a direct .py file
            py_file = module_path.with_suffix('.py')
            if py_file.exists():
                return py_file
            
            return None
        
        # Handle absolute imports
        else:
            # Check if the module is within the project
            module_path = project_root / import_module.replace('.', os.sep)
            
            # Check if this path is a directory with an __init__.py
            if module_path.is_dir():
                init_file = module_path / "__init__.py"
                if init_file.exists():
                    return init_file
            
            # Or try as a direct .py file
            py_file = module_path.with_suffix('.py')
            if py_file.exists():
                return py_file
            
            # Try to find it by searching all Python files that match the module name
            for py_file in project_root.rglob(f"{module_path.name}.py"):
                if py_file.exists():
                    return py_file
    
        return None
    
    def _visualize_dependency_graph(self, graph: nx.DiGraph, output_path: str):
        """Visualize the dependency graph using matplotlib."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            
            # Set up the plot
            plt.figure(figsize=(12, 8))
            
            # Choose layout
            if self.config.graph_layout == "spring":
                pos = nx.spring_layout(graph, k=3, iterations=50)
            elif self.config.graph_layout == "circular":
                pos = nx.circular_layout(graph)
            elif self.config.graph_layout == "random":
                pos = nx.random_layout(graph)
            else:
                pos = nx.spring_layout(graph)
            
            # Draw nodes with different colors based on type
            node_colors = []
            for node in graph.nodes():
                node_colors.append(self.config.file_node_color)
            
            # Draw the graph
            nx.draw_networkx_nodes(
                graph, pos, 
                node_color=node_colors,
                node_size=self.config.node_size,
                alpha=0.7
            )
            
            nx.draw_networkx_edges(
                graph, pos,
                edge_color=self.config.dependency_edge_color,
                arrows=True,
                arrowsize=20,
                edge_cmap=plt.cm.Blues,
                width=1.0
            )
            
            # Draw labels
            nx.draw_networkx_labels(
                graph, pos,
                font_size=self.config.font_size,
                font_weight=self.config.font_weight
            )
            
            # Create legend
            file_patch = mpatches.Patch(color=self.config.file_node_color, label='Python Files')
            plt.legend(handles=[file_patch], loc='upper right')
            
            # Add title
            plt.title("Project Dependency Graph", size=14, weight='bold')
            
            # Save and close
            plt.savefig(output_path, dpi=self.config.dpi, bbox_inches='tight')
            plt.close()
        
        except ImportError:
            # If matplotlib is not available, create a text representation
            with open(output_path.replace('.' + self.config.file_format, '.txt'), 'w') as f:
                f.write("Dependency Graph (text representation):\n\n")
                for node in graph.nodes():
                    f.write(f"File: {node}\n")
                    imports = list(graph.successors(node))
                    if imports:
                        f.write(f"  Imports: {', '.join(imports)}\n")
                    imported_by = list(graph.predecessors(node))
                    if imported_by:
                        f.write(f"  Imported by: {', '.join(imported_by)}\n")
                    f.write("\n")
    
    def generate_project_structure(self, project_path: Optional[str] = None) -> str:
        """Generate a visualization of the project structure."""
        if project_path is None:
            project_path = str(self.workspace_root)

        project_root = Path(project_path)

        # Create a hierarchical representation of the project
        structure = self._build_project_structure(project_root)

        # Create an HTML visualization of the project structure
        output_file = self.output_path / f"project_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        self._create_project_structure_html(structure, str(output_file))

        return f"Project structure visualization saved to: {output_file}"

    def _create_project_structure_html(self, structure: Dict[str, Any], output_path: str):
        """Create an HTML visualization of the project structure."""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Project Structure Visualization</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; color: #2c3e50; }
        .tree { margin-left: 20px; }
        .folder {
            color: #2980b9;
            font-weight: bold;
            margin: 5px 0;
            cursor: pointer;
            display: block;
        }
        .file {
            color: #27ae60;
            margin: 3px 0;
            display: block;
            padding-left: 20px;
        }
        .file-size {
            font-size: 0.8em;
            color: #7f8c8d;
            margin-left: 5px;
        }
        .collapsed { display: none; }
        .toggle { margin-right: 5px; cursor: pointer; }
        .info-box {
            background: #eaf2f8;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #3498db;
        }
    </style>
    <script>
        function toggleFolder(element) {
            const content = element.nextElementSibling;
            if (content.classList.contains('collapsed')) {
                content.classList.remove('collapsed');
                element.innerHTML = '▼ ';
            } else {
                content.classList.add('collapsed');
                element.innerHTML = '▶ ';
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📁 Project Structure</h1>
            <p>Visual representation of your project hierarchy</p>
        </div>
        <div class="info-box">
            <p><strong>Tip:</strong> Click on folder icons to expand/collapse directories</p>
        </div>
        <div class="tree">
        """

        # Add project root
        html_content += f'<div class="folder" onclick="toggleFolder(this)"><span class="toggle">▼ </span>{structure["name"]}/</div>\n'
        html_content += '<div class="tree-content">\n'

        # Add children
        for child in sorted(structure['children'], key=lambda x: (x['type'] != 'directory', x['name'])):
            html_content += self._render_tree_node(child, 1)

        html_content += """
        </div>
        </div>
    </div>
</body>
</html>
        """

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _render_tree_node(self, node: Dict[str, Any], depth: int) -> str:
        """Render a single node in the project structure tree."""
        indent = "  " * depth
        result = ""

        if node['type'] == 'directory':
            result += f'{indent}<div class="folder" onclick="toggleFolder(this)"><span class="toggle">▼ </span>{node["name"]}/</div>\n'
            result += f'{indent}<div class="tree-content" style="margin-left: 20px;">\n'

            for child in sorted(node['children'], key=lambda x: (x['type'] != 'directory', x['name'])):
                result += self._render_tree_node(child, depth + 1)

            result += f'{indent}</div>\n'
        else:
            size_str = self._format_file_size(node.get('size', 0))
            result += f'{indent}<div class="file">{node["name"]} <span class="file-size">({size_str})</span></div>\n'

        return result
    
    def _build_project_structure(self, project_root: Path) -> Dict[str, Any]:
        """Build a hierarchical representation of the project structure."""
        structure = {
            "name": project_root.name,
            "path": str(project_root),
            "type": "directory",
            "children": []
        }
        
        # Add files and directories
        for item in project_root.iterdir():
            if item.name.startswith('.') or item.name == '__pycache__':
                continue  # Skip hidden files/dirs and Python cache
            
            if item.is_dir():
                # Recursively add directory
                child_structure = self._build_project_structure(item)
                structure["children"].append(child_structure)
            elif item.is_file():
                # Add file
                structure["children"].append({
                    "name": item.name,
                    "path": str(item),
                    "type": "file",
                    "size": item.stat().st_size
                })
        
        return structure
    
    def _write_project_structure(self, structure: Dict[str, Any], file, depth: int = 0):
        """Write the project structure to a file with indentation."""
        indent = "  " * depth
        file.write(f"{indent}{structure['name']}/\n")
        
        for child in sorted(structure['children'], key=lambda x: x['name']):
            if child['type'] == 'directory':
                self._write_project_structure(child, file, depth + 1)
            else:
                size_str = self._format_file_size(child.get('size', 0))
                file.write(f"{indent}  {child['name']} ({size_str})\n")
    
    def _format_file_size(self, size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def generate_performance_dashboard(self) -> str:
        """Generate a performance metrics dashboard."""
        # Gather various metrics about the project
        metrics = self._gather_performance_metrics()
        
        # Create dashboard output
        output_file = self.output_path / f"performance_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        self._create_performance_dashboard(metrics, str(output_file))
        
        return f"Performance dashboard saved to: {output_file}"
    
    def _gather_performance_metrics(self) -> Dict[str, Any]:
        """Gather various performance metrics about the project."""
        project_stats = {
            "total_files": 0,
            "python_files": 0,
            "total_lines": 0,
            "total_size": 0,
            "directories": 0,
            "file_extensions": {},
            "complexity_metrics": {
                "total_functions": 0,
                "total_classes": 0
            }
        }
        
        for file_path in self.workspace_root.rglob("*"):
            if file_path.is_file():
                if file_path.name.startswith('.'):
                    continue  # Skip hidden files
                
                stat = file_path.stat()
                project_stats["total_size"] += stat.st_size
                
                ext = file_path.suffix.lower()
                project_stats["file_extensions"][ext] = project_stats["file_extensions"].get(ext, 0) + 1
                project_stats["total_files"] += 1
                
                if ext == ".py":
                    project_stats["python_files"] += 1
                    
                    # Count lines
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            project_stats["total_lines"] += len(lines)
                    except:
                        pass  # Skip if can't read file
                    
                    # Count functions and classes
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Simple pattern matching for functions and classes
                            import re
                            functions = re.findall(r'^\s*def\s+\w+\s*\(', content, re.MULTILINE)
                            classes = re.findall(r'^\s*class\s+\w+', content, re.MULTILINE)
                            project_stats["complexity_metrics"]["total_functions"] += len(functions)
                            project_stats["complexity_metrics"]["total_classes"] += len(classes)
                    except:
                        pass  # Skip if can't read file
            elif file_path.is_dir():
                if file_path.name != '__pycache__':
                    project_stats["directories"] += 1
        
        return project_stats
    
    def _create_performance_dashboard(self, metrics: Dict[str, Any], output_path: str):
        """Create an HTML dashboard for performance metrics."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Project Performance Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .dashboard {{ max-width: 800px; margin: 0 auto; }}
        .metric {{ 
            background: #f4f4f4; 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 5px; 
            border-left: 4px solid #3498db;
        }}
        .header {{ 
            background: #2c3e50; 
            color: white; 
            padding: 20px; 
            text-align: center; 
            border-radius: 5px; 
            margin-bottom: 20px;
        }}
        .subheader {{ 
            background: #3498db; 
            color: white; 
            padding: 10px; 
            margin: 15px 0 5px 0; 
            border-radius: 3px;
        }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>Project Performance Dashboard</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="metric">
            <h3>📁 Project Overview</h3>
            <p><strong>Total Files:</strong> {metrics['total_files']}</p>
            <p><strong>Python Files:</strong> {metrics['python_files']}</p>
            <p><strong>Directories:</strong> {metrics['directories']}</p>
            <p><strong>Total Lines of Code:</strong> {metrics['total_lines']:,}</p>
            <p><strong>Total Size:</strong> {self._format_file_size(metrics['total_size'])}</p>
        </div>
        
        <div class="metric">
            <h3>📊 Code Structure</h3>
            <p><strong>Total Functions:</strong> {metrics['complexity_metrics']['total_functions']}</p>
            <p><strong>Total Classes:</strong> {metrics['complexity_metrics']['total_classes']}</p>
        </div>
        
        <div class="metric">
            <h3>📝 File Extensions</h3>
            <ul>
        """
        
        for ext, count in sorted(metrics['file_extensions'].items(), key=lambda x: x[1], reverse=True):
            html_content += f"<li><strong>{ext}:</strong> {count} files</li>\n"
        
        html_content += """
            </ul>
        </div>
        
        <div class="subheader">
            <h3>💡 Analysis Tips</h3>
        </div>
        <div class="metric">
        """
        
        # Add insights based on metrics
        if metrics['python_files'] > 50:
            html_content += "<p>📝 <strong>Large codebase:</strong> Consider modularizing your code further.</p>\n"
        
        if metrics['complexity_metrics']['total_functions'] / max(metrics['python_files'], 1) > 10:
            html_content += "<p>🔧 <strong>Function density:</strong> Consider refactoring files with too many functions.</p>\n"
        
        if metrics['total_lines'] / max(metrics['python_files'], 1) > 500:
            html_content += "<p>📈 <strong>Large files:</strong> Consider splitting large files into smaller modules.</p>\n"
        
        html_content += """
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)