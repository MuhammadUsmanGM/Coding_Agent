"""
Automated Testing Tool
Runs local pytest and returns summary results.
"""
from flask import Flask, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/test', methods=['POST'])
def test():
    # Run pytest with safe parameters
    try:
        # Change to the project directory to run tests
        proc = subprocess.run(
            ['python', '-m', 'pytest', '--maxfail=1', '--disable-warnings', '--tb=short', '-v'], 
            capture_output=True, 
            text=True,
            timeout=120,  # 2 minute timeout
            cwd=os.getcwd()  # Run in current directory
        )
        return jsonify({
            'stdout': proc.stdout, 
            'stderr': proc.stderr,
            'returncode': proc.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Test execution timed out'}), 400
    except FileNotFoundError:
        return jsonify({'error': 'pytest not found, please install pytest'}), 400
    except Exception as e:
        return jsonify({'error': f'Test execution failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=9500)