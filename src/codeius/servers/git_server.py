"""
GitHub/Git MCP Server
Handles version control operations like push, pull, clone, branch management, etc.
"""
from flask import Flask, request, jsonify
import subprocess
import os
import json
from pathlib import Path


app = Flask(__name__)

def run_git_command(command, cwd=None):
    """Run a git command in the specified directory"""
    try:
        # Execute using subprocess in the specified directory
        result = subprocess.run(
            command,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout for git operations
        )
        if result.returncode == 0:
            return {"output": result.stdout, "error": result.stderr if result.stderr else None, "success": True}
        else:
            return {"output": result.stdout, "error": result.stderr, "success": False}
    except subprocess.TimeoutExpired:
        return {"error": "Git command timed out", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.route('/status', methods=['GET'])
def git_status():
    """Get the git status of the current repository"""
    repo_path = request.args.get('repo_path', os.getcwd())
    result = run_git_command(['git', 'status', '--porcelain'], cwd=repo_path)
    return jsonify(result)


@app.route('/add', methods=['POST'])
def git_add():
    """Add files to git staging area"""
    data = request.json
    files = data.get('files', '.')
    repo_path = data.get('repo_path', os.getcwd())

    if isinstance(files, list):
        # Add multiple files
        for file in files:
            result = run_git_command(['git', 'add', file], cwd=repo_path)
            if not result['success']:
                return jsonify(result)
        return jsonify({"output": f"Added {len(files)} files to staging area", "success": True})
    else:
        # Add single file or all files (if '.' is passed)
        result = run_git_command(['git', 'add', files], cwd=repo_path)
        return jsonify(result)


@app.route('/commit', methods=['POST'])
def git_commit():
    """Commit staged changes"""
    data = request.json
    message = data.get('message', 'Auto-commit from Codeius')
    repo_path = data.get('repo_path', os.getcwd())

    result = run_git_command(['git', 'commit', '-m', message], cwd=repo_path)
    return jsonify(result)


@app.route('/push', methods=['POST'])
def git_push():
    """Push changes to remote repository"""
    data = request.json
    remote = data.get('remote', 'origin')
    branch = data.get('branch', 'main')  # Default to 'main' instead of 'master'
    repo_path = data.get('repo_path', os.getcwd())

    result = run_git_command(['git', 'push', remote, branch], cwd=repo_path)
    return jsonify(result)


@app.route('/pull', methods=['POST'])
def git_pull():
    """Pull changes from remote repository"""
    data = request.json
    remote = data.get('remote', 'origin')
    branch = data.get('branch', 'main')  # Default to 'main' instead of 'master'
    repo_path = data.get('repo_path', os.getcwd())

    result = run_git_command(['git', 'pull', remote, branch], cwd=repo_path)
    return jsonify(result)


@app.route('/clone', methods=['POST'])
def git_clone():
    """Clone a remote repository"""
    data = request.json
    url = data.get('url')
    destination = data.get('destination', os.getcwd())

    if not url:
        return jsonify({"error": "Repository URL is required", "success": False}), 400

    result = run_git_command(['git', 'clone', url, destination])
    return jsonify(result)


@app.route('/branch', methods=['GET', 'POST'])
def git_branch():
    """List, create, or switch branches"""
    if request.method == 'GET':
        # List branches
        repo_path = request.args.get('repo_path', os.getcwd())
        result = run_git_command(['git', 'branch', '-a'], cwd=repo_path)
        return jsonify(result)

    elif request.method == 'POST':
        # Create or switch branch
        data = request.json
        repo_path = data.get('repo_path', os.getcwd())

        if 'create' in data:
            # Create a new branch
            branch_name = data['create']
            result = run_git_command(['git', 'checkout', '-b', branch_name], cwd=repo_path)
            return jsonify(result)
        elif 'switch' in data:
            # Switch to an existing branch
            branch_name = data['switch']
            result = run_git_command(['git', 'checkout', branch_name], cwd=repo_path)
            return jsonify(result)
        else:
            return jsonify({"error": "Specify either 'create' or 'switch' parameter", "success": False}), 400


@app.route('/log', methods=['GET'])
def git_log():
    """Show git log"""
    repo_path = request.args.get('repo_path', os.getcwd())
    limit = request.args.get('limit', '10')  # Default to last 10 commits

    result = run_git_command(['git', 'log', '--oneline', '-n', limit], cwd=repo_path)
    return jsonify(result)


@app.route('/diff', methods=['GET'])
def git_diff():
    """Show git diff"""
    repo_path = request.args.get('repo_path', os.getcwd())
    staged = request.args.get('staged', 'false').lower() == 'true'

    if staged:
        command = ['git', 'diff', '--cached']
    else:
        command = ['git', 'diff']

    result = run_git_command(command, cwd=repo_path)
    return jsonify(result)


@app.route('/remote', methods=['GET', 'POST'])
def git_remote():
    """Manage git remotes"""
    if request.method == 'GET':
        # List remotes
        repo_path = request.args.get('repo_path', os.getcwd())
        result = run_git_command(['git', 'remote', '-v'], cwd=repo_path)
        return jsonify(result)

    elif request.method == 'POST':
        # Add or update remote
        data = request.json
        repo_path = data.get('repo_path', os.getcwd())

        if 'add' in data:
            name = data['add']
            url = data['url']
            result = run_git_command(['git', 'remote', 'add', name, url], cwd=repo_path)
        elif 'set_url' in data:
            name = data['set_url']
            url = data['url']
            result = run_git_command(['git', 'remote', 'set-url', name, url], cwd=repo_path)
        else:
            return jsonify({"error": "Specify either 'add' or 'set_url' parameter", "success": False}), 400

        return jsonify(result)


@app.route('/init', methods=['POST'])
def git_init():
    """Initialize a new git repository"""
    data = request.json
    repo_path = data.get('repo_path', os.getcwd())
    bare = data.get('bare', False)

    command = ['git', 'init']
    if bare:
        command.append('--bare')

    result = run_git_command(command, cwd=repo_path)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10100, debug=False)