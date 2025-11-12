"""
Shell/Terminal Tool
Safely executes local shell commands (with strict restrictions).
"""
from flask import Flask, request, jsonify
import subprocess
import shlex

app = Flask(__name__)

SAFE_CMDS = ['ls', 'dir', 'cat', 'type', 'pwd', 'echo', 'grep', 'find', 'python', 'pytest', 'pip', 'git']

@app.route('/shell', methods=['POST'])
def shell():
    cmd_str = request.json.get('cmd', '')
    if not cmd_str:
        return jsonify({'error': 'No command provided'}), 400
    
    # Split the command safely
    try:
        cmd = shlex.split(cmd_str)
    except ValueError as e:
        return jsonify({'error': f'Invalid command format: {str(e)}'}), 400
    
    if cmd and cmd[0] in SAFE_CMDS:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return jsonify({
                'stdout': proc.stdout, 
                'stderr': proc.stderr,
                'returncode': proc.returncode
            })
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Command timed out'}), 400
        except Exception as e:
            return jsonify({'error': f'Command execution failed: {str(e)}'}), 500
    return jsonify({'error': 'Unsafe or unknown command'}), 400

if __name__ == '__main__':
    app.run(port=9400)