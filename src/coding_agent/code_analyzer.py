"""
Code analysis and linting service for Codeius AI Coding Agent.
Provides code quality checks and suggestions.
"""
import ast
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from coding_agent.logger import agent_logger
from coding_agent.error_handler import handle_error, handle_success, ErrorCode
import subprocess
import sys


class CodeAnalyzer:
    """Analyzes code for quality, security, and style issues."""
    
    def __init__(self):
        self.supported_languages = {'.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json', '.md'}
    
    def analyze_code(self, file_path: str, content: Optional[str] = None) -> Dict[str, Any]:
        """Analyze code in a file for issues."""
        try:
            # Read file if content not provided
            if content is None:
                from coding_agent.file_ops import FileOps
                file_ops = FileOps()
                content = file_ops.read_file(file_path)
                
                if content.startswith("Error:"):
                    agent_logger.app_logger.error(f"Could not read file for analysis: {content}")
                    return {"errors": [f"Could not read file: {content}"]}
            
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.py':
                return self._analyze_python(content, file_path)
            elif file_ext in {'.js', '.jsx', '.ts', '.tsx'}:
                return self._analyze_javascript(content, file_path)
            elif file_ext in {'.html', '.css'}:
                return self._analyze_web(content, file_path)
            else:
                # For other file types, do basic checks
                return self._analyze_generic(content, file_path)
                
        except Exception as e:
            agent_logger.app_logger.error(f"Error analyzing code in {file_path}: {str(e)}")
            return {"errors": [f"Analysis failed: {str(e)}"]}
    
    def _analyze_python(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Python code using AST and other tools."""
        issues = []
        metrics = {}
        
        try:
            # Parse AST to check for syntax errors
            tree = ast.parse(content)
            
            # Analyze the AST for potential issues
            issues.extend(self._analyze_python_ast(tree, content))
            
            # Check for complexity
            complexity = self._calculate_python_complexity(tree)
            metrics["cyclomatic_complexity"] = complexity
            
            # Run flake8 if available for more detailed analysis
            try:
                result = subprocess.run([
                    sys.executable, "-m", "flake8", 
                    "--format=json", 
                    "--max-line-length=120"
                ], input=content, text=True, capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    # No issues found by flake8
                    pass
                else:
                    # Parse flake8 results
                    flake8_issues = self._parse_flake8_output(result.stdout)
                    issues.extend(flake8_issues)
            except subprocess.TimeoutExpired:
                agent_logger.app_logger.warning("Flake8 analysis timed out")
            except Exception:
                # Flake8 might not be installed, continue with basic analysis
                agent_logger.app_logger.debug("Flake8 not available, using basic analysis only")
            
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "message": f"Syntax error: {str(e)}",
                "line": e.lineno or 0,
                "column": e.offset or 0
            })
        except Exception as e:
            issues.append({
                "type": "analysis_error", 
                "message": f"Analysis error: {str(e)}"
            })
        
        return {
            "issues": issues,
            "metrics": metrics,
            "summary": {
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.get("severity") == "critical"]),
                "warnings": len([i for i in issues if i.get("severity") == "warning"])
            }
        }
    
    def _analyze_python_ast(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Analyze Python AST for potential issues."""
        issues = []
        lines = content.splitlines()
        
        # Walk through AST nodes
        for node in ast.walk(tree):
            # Check for common issues
            if isinstance(node, ast.ImportFrom) and node.module == "typing" and node.level == 0:
                # This is a normal typing import, not an issue
                pass
            elif isinstance(node, ast.Import) and any(alias.name == "os" and any(n.startswith('system') or n == 'popen' for n in [name for name in dir(__import__(alias.name)) if not name.startswith('_')] if alias.name in sys.modules) for alias in node.names):
                # Check for potential security issues with os.system, os.popen, etc.
                issues.append({
                    "type": "security",
                    "message": "Potential security issue: use of os.system/popen detected",
                    "line": node.lineno,
                    "severity": "critical"
                })
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "eval":
                issues.append({
                    "type": "security",
                    "message": "Dangerous use of eval() function",
                    "line": node.lineno,
                    "severity": "critical"
                })
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "exec":
                issues.append({
                    "type": "security",
                    "message": "Dangerous use of exec() function",
                    "line": node.lineno,
                    "severity": "critical"
                })
            elif isinstance(node, ast.Assert):
                issues.append({
                    "type": "style",
                    "message": "Using assert for production code is not recommended",
                    "line": node.lineno,
                    "severity": "warning"
                })
        
        return issues
        
    def _calculate_python_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity of Python code."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):  # and, or
                complexity += len(node.values) - 1
        
        return complexity
    
    def _parse_flake8_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse flake8 JSON output."""
        issues = []
        try:
            results = json.loads(output)
            for result in results:
                issues.append({
                    "type": "style",
                    "message": result.get("message", "Style issue detected"),
                    "line": result.get("line_number", 0),
                    "column": result.get("column_number", 0),
                    "code": result.get("error_code", ""),
                    "severity": "warning"
                })
        except:
            # If JSON parsing fails, try to parse as text
            for line in output.splitlines():
                if ':' in line:
                    parts = line.split(':', 3)
                    if len(parts) >= 3:
                        issues.append({
                            "type": "style",
                            "message": parts[3].strip() if len(parts) > 3 else "Style issue detected",
                            "line": int(parts[1]) if parts[1].isdigit() else 0,
                            "column": int(parts[2]) if parts[2].isdigit() else 0,
                            "severity": "warning"
                        })
        return issues
    
    def _analyze_javascript(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code."""
        issues = []
        metrics = {}
        
        # Basic analysis for JS/TS
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if "eval(" in line:
                issues.append({
                    "type": "security",
                    "message": "Dangerous use of eval() function",
                    "line": i,
                    "severity": "critical"
                })
            elif "document.write" in line:
                issues.append({
                    "type": "security", 
                    "message": "Using document.write can be dangerous",
                    "line": i,
                    "severity": "warning"
                })
            elif "innerHTML" in line:
                issues.append({
                    "type": "security",
                    "message": "innerHTML can lead to XSS vulnerabilities",
                    "line": i,
                    "severity": "warning"
                })
        
        return {
            "issues": issues,
            "metrics": metrics,
            "summary": {
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.get("severity") == "critical"]),
                "warnings": len([i for i in issues if i.get("severity") == "warning"])
            }
        }
    
    def _analyze_web(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze HTML/CSS code."""
        issues = []
        metrics = {}
        
        # Basic analysis for web files
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if "<script>" in line.lower() and "src=" not in line.lower():
                issues.append({
                    "type": "security",
                    "message": "Inline JavaScript detected",
                    "line": i,
                    "severity": "warning"
                })
            elif 'javascript:' in line.lower():
                issues.append({
                    "type": "security",
                    "message": "JavaScript protocol detected in HTML",
                    "line": i,
                    "severity": "critical"
                })
        
        return {
            "issues": issues,
            "metrics": metrics,
            "summary": {
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.get("severity") == "critical"]),
                "warnings": len([i for i in issues if i.get("severity") == "warning"])
            }
        }
    
    def _analyze_generic(self, content: str, file_path: str) -> Dict[str, Any]:
        """Basic analysis for other file types."""
        issues = []
        metrics = {}
        
        # Check for common issues in any text file
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            if len(line) > 120:  # Line too long
                issues.append({
                    "type": "style",
                    "message": "Line too long (recommended: < 120 characters)",
                    "line": i,
                    "severity": "warning"
                })
            if line.endswith(" "):  # Trailing whitespace
                issues.append({
                    "type": "style",
                    "message": "Trailing whitespace detected",
                    "line": i,
                    "severity": "warning"
                })
        
        return {
            "issues": issues,
            "metrics": metrics,
            "summary": {
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.get("severity") == "critical"]),
                "warnings": len([i for i in issues if i.get("severity") == "warning"])
            }
        }
    
    def get_code_suggestions(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on code analysis."""
        suggestions = []
        
        for issue in analysis_result.get("issues", []):
            if issue.get("type") == "security" and issue.get("severity") == "critical":
                suggestions.append(f"Fix critical security issue on line {issue.get('line', 'unknown')}: {issue.get('message')}")
            elif issue.get("type") == "style":
                suggestions.append(f"Improve code style on line {issue.get('line', 'unknown')}: {issue.get('message')}")
        
        if not suggestions:
            suggestions.append("Code looks good! No major issues detected.")
        
        return suggestions