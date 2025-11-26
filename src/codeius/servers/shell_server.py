"""
Shell/Terminal Tool
Safely executes local shell commands (with strict restrictions).
"""
from flask import Flask, request, jsonify
import subprocess
import shlex
import asyncio

app = Flask(__name__)

SAFE_CMDS = ['ls', 'dir', 'cat', 'type', 'pwd', 'echo', 'grep', 'find', 'python', 'pytest', 'pip', 'git']

@app.route('/shell', methods=['POST'])
async def shell():
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
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                text=True
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            return jsonify({
                'stdout': stdout,
                'stderr': stderr,
                'returncode': process.returncode
            })
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return jsonify({'error': 'Command timed out'}), 400
        except Exception as e:
            return jsonify({'error': f'Command execution failed: {str(e)}'}), 500
    return jsonify({'error': 'Unsafe or unknown command'}), 400

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9400)