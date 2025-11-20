"""
Project Analyzer for the CodingAgent.
Analyzes the entire project structure and content to provide insights.
"""
import os
import json
from typing import Dict, List, Any
from pathlib import Path


class ProjectAnalyzer:
    """Analyzes project structure and content."""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.project_info = {
            "name": self.root_path.name,
            "path": str(self.root_path.absolute()),
            "files": [],
            "directories": [],
            "languages": {},
            "total_files": 0,
            "total_lines": 0
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analyze the entire project."""
        print(f"🔍 Starting analysis of project: {self.project_info['name']}")
        
        # Walk through the project and collect information
        for root, dirs, files in os.walk(self.root_path):
            # Skip common directories that shouldn't be analyzed
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', '.venv', 'env']]
            
            relative_root = Path(root).relative_to(self.root_path)
            
            # Add directories
            for directory in dirs:
                dir_path = relative_root / directory
                self.project_info["directories"].append(str(dir_path))
            
            # Process files
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.root_path)
                
                # Skip common files that shouldn't be analyzed
                if file.startswith('.') or file.endswith(('.pyc', '.pyo', '.log', '.tmp')):
                    continue
                
                # Add file to project info
                file_info = {
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix
                }
                
                self.project_info["files"].append(file_info)
                self.project_info["total_files"] += 1
                
                # Count lines if it's a text file
                if self._is_text_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            file_info["lines"] = len(lines)
                            self.project_info["total_lines"] += len(lines)
                            
                            # Determine language
                            lang = self._get_language_from_extension(file_path.suffix)
                            if lang:
                                self.project_info["languages"][lang] = self.project_info["languages"].get(lang, 0) + 1
                    except:
                        # If we can't read the file, skip line counting
                        pass
        
        print(f"✅ Analysis complete. Found {self.project_info['total_files']} files in {len(self.project_info['directories'])} directories.")
        return self.project_info
    
    def generate_analysis_report(self) -> str:
        """Generate a human-readable analysis report."""
        if not self.project_info["files"]:
            return "❌ No files found in the project directory."
        
        report = []
        report.append(f"## 📁 Project Analysis: {self.project_info['name']}")
        report.append("")
        report.append(f"**Path**: `{self.project_info['path']}`")
        report.append(f"**Total Files**: {self.project_info['total_files']}")
        report.append(f"**Total Lines**: {self.project_info['total_lines']:,}")
        report.append("")
        
        # Languages breakdown
        if self.project_info["languages"]:
            report.append("### 🧮 Languages Breakdown")
            for lang, count in sorted(self.project_info["languages"].items(), key=lambda x: x[1], reverse=True):
                report.append(f"- {lang}: {count} files")
            report.append("")
        
        # Top files by line count
        text_files = [f for f in self.project_info["files"] if "lines" in f]
        if text_files:
            top_files = sorted(text_files, key=lambda x: x.get("lines", 0), reverse=True)[:10]
            report.append("### 📄 Top 10 Largest Files")
            for file_info in top_files:
                report.append(f"- `{file_info['path']}`: {file_info.get('lines', 0):,} lines")
            report.append("")
        
        # Directory structure (top level only to keep it manageable)
        top_level_dirs = [d for d in self.project_info["directories"] if '/' not in d and '\\' not in d]
        if top_level_dirs:
            report.append("### 📂 Directory Structure (Top Level)")
            for directory in top_level_dirs:
                report.append(f"- `{directory}`")
            report.append("")
        
        # File types
        extensions = {}
        for file_info in self.project_info["files"]:
            ext = file_info["extension"]
            extensions[ext] = extensions.get(ext, 0) + 1
        
        if extensions:
            report.append("### 📋 File Extensions")
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- `{ext}`: {count} files")
            report.append("")
        
        return "\n".join(report)
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if a file is likely a text file."""
        text_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.htm', '.css', '.scss', '.sass',
            '.json', '.xml', '.yaml', '.yml', '.md', '.txt', '.csv', '.sql', '.sh', '.bash',
            '.java', '.cpp', '.c', '.h', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.kts'
        }
        return file_path.suffix.lower() in text_extensions
    
    def _get_language_from_extension(self, extension: str) -> str:
        """Map file extension to programming language."""
        ext_to_lang = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React JSX',
            '.tsx': 'React TSX',
            '.html': 'HTML',
            '.htm': 'HTML',
            '.css': 'CSS',
            '.scss': 'Sass',
            '.json': 'JSON',
            '.xml': 'XML',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.md': 'Markdown',
            '.txt': 'Text',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C Header',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.kts': 'Kotlin Script',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.bash': 'Bash',
            '.csv': 'CSV'
        }
        return ext_to_lang.get(extension.lower(), extension.upper() if extension else "Unknown")


def analyze_current_project() -> str:
    """Convenience function to analyze the current project."""
    analyzer = ProjectAnalyzer()
    analyzer.analyze_project()
    return analyzer.generate_analysis_report()