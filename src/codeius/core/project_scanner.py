"""
Project scanner for analyzing project structure and dependencies.
"""
import os
import json
import re
import fnmatch
from typing import Dict, List

class ProjectScanner:
    def __init__(self):
        self.ignore_patterns = [
            'node_modules', '__pycache__', '*.pyc', '.git',
            'venv', 'env', 'dist', 'build', '.next', '.vscode',
            '*.log', '.DS_Store', 'coverage', '.pytest_cache'
        ]
    
    def scan_directory(self, root_dir: str) -> Dict:
        """Scan project directory and return structure"""
        project_structure = {
            'root': root_dir,
            'files': [],
            'directories': [],
            'total_size': 0
        }
        
        for root, dirs, files in os.walk(root_dir):
            # Filter ignored directories
            dirs[:] = [d for d in dirs if not any(
                fnmatch.fnmatch(d, pattern) for pattern in self.ignore_patterns
            )]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                
                # Skip ignored files
                if any(fnmatch.fnmatch(file, pattern) for pattern in self.ignore_patterns):
                    continue
                
                try:
                    size = os.path.getsize(file_path)
                    ext = os.path.splitext(file)[1]
                    
                    project_structure['files'].append({
                        'path': rel_path.replace('\\', '/'),
                        'name': file,
                        'size': size,
                        'extension': ext
                    })
                    project_structure['total_size'] += size
                except:
                    pass
            
            for dir_name in dirs:
                rel_dir = os.path.relpath(os.path.join(root, dir_name), root_dir)
                project_structure['directories'].append(rel_dir.replace('\\', '/'))
        
        return project_structure
    
    def parse_package_json(self, file_path: str) -> Dict:
        """Parse package.json for JavaScript/Node projects"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return {
                'type': 'javascript',
                'name': data.get('name', 'unknown'),
                'version': data.get('version', '0.0.0'),
                'dependencies': data.get('dependencies', {}),
                'devDependencies': data.get('devDependencies', {})
            }
        except Exception as e:
            return {'error': str(e)}
    
    def parse_requirements_txt(self, file_path: str) -> Dict:
        """Parse requirements.txt for Python projects"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            dependencies = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Parse package==version format
                    match = re.match(r'([a-zA-Z0-9_-]+)(==|>=|<=)?(.+)?', line)
                    if match:
                        dependencies.append({
                            'name': match.group(1),
                            'version': match.group(3) if match.group(3) else 'latest'
                        })
            
            return {
                'type': 'python',
                'dependencies': dependencies
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_project_dependencies(self, project_path: str) -> Dict:
        """Get all project dependencies"""
        dependencies = {}
        
        # Check for JavaScript dependencies
        package_json = os.path.join(project_path, 'package.json')
        if os.path.exists(package_json):
            dependencies['javascript'] = self.parse_package_json(package_json)
        
        # Check for Python dependencies
        requirements_txt = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(requirements_txt):
            dependencies['python'] = self.parse_requirements_txt(requirements_txt)
        
        return dependencies

# Singleton instance
project_scanner = ProjectScanner()
