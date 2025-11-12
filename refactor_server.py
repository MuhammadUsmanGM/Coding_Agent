"""
Code Refactoring & Quality Tool
Analyzes code style, detects anti-patterns, and proposes refactorings.
"""
from flask import Flask, request, jsonify
import tempfile
import os
import subprocess

app = Flask(__name__)

@app.route('/refactor', methods=['POST'])
def refactor():
    # Get file content from request
    content = request.json.get('content', '')
    filename = request.json.get('filename', 'temp.py')
    
    # Create a temporary file with the content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Run basic analysis using Python's AST to detect issues
        import ast
        issues = []
        
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source)
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'message': f"Syntax error at line {e.lineno}: {e.msg}",
                'line': e.lineno
            })
            return jsonify({'issues': issues, 'refactoring_suggestions': []})
        
        # Perform basic analysis
        # Count function definitions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        # Check for long functions (>10 lines)
        for func in functions:
            lines = func.end_lineno - func.lineno
            if lines > 10:
                issues.append({
                    'type': 'long_function',
                    'message': f"Function '{func.name}' is {lines} lines long, consider breaking it down",
                    'line': func.lineno
                })
        
        # Check for unused imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                names.add(node.id)
        
        unused_imports = []
        for imp in imports:
            if isinstance(imp, ast.Import):
                for alias in imp.names:
                    imported_name = alias.asname or alias.name
                    if imported_name not in names:
                        unused_imports.append(imported_name)
            elif isinstance(imp, ast.ImportFrom):
                for alias in imp.names:
                    imported_name = alias.asname or alias.name
                    if imported_name not in names:
                        unused_imports.append(imported_name)
        
        for unused in unused_imports:
            issues.append({
                'type': 'unused_import',
                'message': f"Import '{unused}' is not used",
                'line': imp.lineno if 'imp' in locals() else 1
            })
        
        # Basic refactoring suggestions
        suggestions = []
        if len(functions) > 3:
            suggestions.append("Consider breaking the file into multiple modules for better organization")
        
        if any(len(func.body) > 5 for func in functions):
            suggestions.append("Consider extracting complex functions into smaller helper functions")
        
        return jsonify({
            'issues': issues,
            'refactoring_suggestions': suggestions,
            'function_count': len(functions),
            'class_count': len(classes)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    app.run(port=9900)