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
import pycodestyle
import os
from pyflakes import api as pyflakes_api
import io
from contextlib import redirect_stdout, redirect_stderr


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
            return handle_error(ErrorCode.UNKNOWN_ERROR, f"Analysis failed: {str(e)}").__dict__
    
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

            # Run pycodestyle for style checks
            try:
                style_issues = self._analyze_python_pycodestyle(content, file_path)
                issues.extend(style_issues)
            except Exception:
                agent_logger.app_logger.debug("pycodestyle not available or encountered an error.")

            # Run pyflakes for logical error checks
            try:
                flakes_issues = self._analyze_python_pyflakes(content, file_path)
                issues.extend(flakes_issues)
            except Exception:
                agent_logger.app_logger.debug("pyflakes not available or encountered an error.")
            
            
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

    def _analyze_python_pycodestyle(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze Python code using pycodestyle."""
        style_issues = []
        # Create a Checker instance
        # Suppress stdout/stderr to capture errors directly
        # We'll need a custom reporter to capture the errors
        class CustomReporter(pycodestyle.BaseReport):
            def __init__(self, options):
                super().__init__(options)
                self.results = []

            def error_or_warning(self, line_number, offset, text, check):
                self.results.append({
                    "type": "style",
                    "message": text,
                    "line": line_number,
                    "column": offset,
                    "code": check.code,
                    "severity": "warning"
                })

        # We need a dummy file to pass to pycodestyle if content is from memory
        # Or, we can use a temporary file if file_path is not available
        # For now, let's assume file_path is always provided or we create a temp file.
        # pycodestyle expects a filename to analyze, even if content is passed.
        # This makes it easier for it to resolve configurations like .editorconfig

        # If content is provided and file_path is not, save to a temp file
        temp_file = False
        if file_path == "" or file_path is None:
            import tempfile
            fd, temp_file_path = tempfile.mkstemp(suffix=".py")
            with open(fd, "w") as f:
                f.write(content)
            file_path = temp_file_path
            temp_file = True

        try:
            # pycodestyle expects a list of filenames
            # We can override read_file to use our content, but it's simpler to use a temp file for robustness
            # Or, we can pass the lines directly
            lines = content.splitlines(keepends=True)
            checker = pycodestyle.Checker(filename=file_path, lines=lines, reporter=CustomReporter)
            checker.check_all()
            style_issues.extend(checker.report.results)
        except Exception as e:
            agent_logger.app_logger.warning(f"Error running pycodestyle on {file_path}: {str(e)}", exc_info=True)
        finally:
            if temp_file and os.path.exists(file_path):
                os.remove(file_path)

        return style_issues

    def _analyze_python_pyflakes(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Analyze Python code using pyflakes."""
        pyflakes_issues = []
        try:
            # pyflakes expects a file-like object or a filename
            # We will use a StringIO to pass content directly
            import io
            from contextlib import redirect_stdout, redirect_stderr

            # Capture stdout and stderr from pyflakes
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()

            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                # pyflakes_api.check expects a file path as its first argument
                # and then a file-like object for input if content is not from a real file.
                # If file_path is None or empty, create a dummy name for pyflakes
                if not file_path:
                    file_path = "<stdin>.py"

                # pyflakes_api.check returns the number of errors
                # but the detailed messages are printed to stderr
                pyflakes_api.check(io.StringIO(content), file_path)

            # Process captured stderr for issues
            for line in stderr_capture.getvalue().splitlines():
                # pyflakes output format: filename:line:column: message
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    try:
                        line_num = int(parts[1])
                        col_num = int(parts[2])
                        message = parts[3].strip()
                        pyflakes_issues.append({
                            "type": "error", # pyflakes typically reports errors or warnings
                            "message": message,
                            "line": line_num,
                            "column": col_num,
                            "code": "", # pyflakes doesn't provide explicit error codes like flake8
                            "severity": "error" if "Undefined name" in message or "syntax error" in message.lower() else "warning"
                        })
                    except ValueError:
                        agent_logger.app_logger.warning(f"Could not parse pyflakes output line: {line}")
                else:
                    agent_logger.app_logger.warning(f"Unexpected pyflakes output format: {line}")

        except Exception as e:
            agent_logger.app_logger.warning(f"Error running pyflakes on {file_path}: {str(e)}", exc_info=True)

        return pyflakes_issues

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
        except Exception as e:
            agent_logger.app_logger.warning(f"Error parsing flake8 output as JSON: {e}. Attempting text parse.", exc_info=True)
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