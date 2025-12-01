# api/server.py

import os
import socket
from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from codeius.core.agent import CodingAgent

# Get the directory of this file and go up to project root, then to Codeius-GUI
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

# Look for the dist folder in the correct location relative to the project
codeius_gui_dir = os.path.join(project_root, 'Codeius-GUI')
dist_path = os.path.join(codeius_gui_dir, 'dist')

# Check if we're in development mode (dist may not exist) or if the path is different


# If the standard path doesn't exist, try to find it relative to the current working directory
if not os.path.exists(dist_path):
    # Try to find the Codeius-GUI directory in the current working directory parent
    import sys
    import pathlib
    # Get the project root (where pyproject.toml would be)
    possible_roots = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))), 'Codeius-GUI', 'dist'),  # Go up 3 levels
        os.path.join(os.path.dirname(os.path.dirname(current_dir)), '..', 'Codeius-GUI', 'dist'),  # Go up 2, then up 1 more
        os.path.join('.', 'Codeius-GUI', 'dist'),  # Same level as project root
        os.path.join('..', 'Codeius-GUI', 'dist'),  # One level up
    ]

    for path in possible_roots:
        abs_path = os.path.abspath(path)

        if os.path.exists(abs_path):
            dist_path = abs_path
            break

# Now create the Flask app based on whether the dist folder exists
if os.path.exists(dist_path):
    # Store the found dist path in a variable that the app can use
    final_dist_path = dist_path
    app = Flask(__name__,
               static_folder=final_dist_path,  # Path to built React app
               template_folder=final_dist_path)

else:
    final_dist_path = None
    # If no production build, create app without static folder
    app = Flask(__name__)


CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:*", "http://127.0.0.1:*"])
agent = CodingAgent()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Check if static folder exists (the built React app)
    if app.static_folder and os.path.exists(app.static_folder):
        # If a specific file is requested, try to serve it
        if path:
            static_path = os.path.join(app.static_folder, path)
            if os.path.exists(static_path):
                return send_from_directory(app.static_folder, path)
            else:
                # If the file doesn't exist, serve index.html for client-side routing
                return send_from_directory(app.static_folder, 'index.html')
        else:
            # If root path, serve the main index.html
            return send_from_directory(app.static_folder, 'index.html')
    else:
        # If no static folder exists, return a page with instructions
        # (This would only happen if the React app hasn't been built yet)
        return '''
        <h1 style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px; color: #333;">
            Codeius Web Interface
        </h1>
        <div style="font-family: Arial, sans-serif; text-align: center; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <p style="font-size: 18px; color: #555;">
                To use the full web interface, you have two options:
            </p>
            <div style="margin: 20px 0;">
                <h3 style="color: #007acc;">Option 1: Production Build</h3>
                <p>Run this command in the Codeius-GUI directory:</p>
                <code style="background: #eef; padding: 8px; border-radius: 4px; display: inline-block;">npm run build</code>
            </div>
            <div style="margin: 20px 0;">
                <h3 style="color: #007acc;">Option 2: Development Mode</h3>
                <p>Run this command in the Codeius-GUI directory:</p>
                <code style="background: #eef; padding: 8px; border-radius: 4px; display: inline-block;">npm run dev</code>
                <p style="margin-top: 10px;">Then access the interface at <a href="http://localhost:3000" target="_blank">http://localhost:3000</a></p>
            </div>
            <p style="margin-top: 20px; font-style: italic; color: #888;">
                The backend API is running on this server and will be accessible to the web interface.
            </p>
        </div>
        '''

@app.route('/api/models')
def models():
    """Get available models"""
    try:
        model_list = agent.get_available_models()

        # Handle different possible formats of model data
        if isinstance(model_list, dict):
            # If it's a dictionary format {key: model_obj_or_dict}
            serializable_models = {}
            for key, model_data in model_list.items():
                if hasattr(model_data, 'name') and hasattr(model_data, 'key'):
                    # If it's an object with name/key attributes
                    serializable_models[key] = {
                        "name": getattr(model_data, 'name', key),
                        "provider": getattr(model_data, 'provider', 'unknown'),
                        "description": getattr(model_data, 'description', '')
                    }
                elif isinstance(model_data, dict):
                    # If it's already a dictionary
                    serializable_models[key] = {
                        "name": model_data.get('name', key),
                        "provider": model_data.get('provider', 'unknown'),
                        "description": model_data.get('description', '')
                    }
                else:
                    # Fallback for other formats
                    serializable_models[key] = {
                        "name": str(model_data),
                        "provider": "unknown",
                        "description": ""
                    }
        elif isinstance(model_list, (list, tuple)):
            # If it's a list/tuple of model objects
            serializable_models = {}
            for model in model_list:
                if hasattr(model, 'key') and hasattr(model, 'name'):
                    key = getattr(model, 'key', str(id(model)))
                    serializable_models[key] = {
                        "name": getattr(model, 'name', 'Unknown'),
                        "provider": getattr(model, 'provider', 'unknown'),
                        "description": getattr(model, 'description', '')
                    }
        else:
            # Fallback for other formats
            print(f"Unexpected model list format: {type(model_list)}")
            serializable_models = {}

        return jsonify({'models': serializable_models})
    except Exception as e:
        print(f"Error in /api/models endpoint: {str(e)}")
        return jsonify({'error': 'Failed to get models', 'details': str(e)}), 500

@app.route('/api/ask', methods=['POST'])
def ask():
    """Ask the AI assistant"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        # Show thinking indicator via socket
        socketio.emit('agent_thinking', {'thinking': True})
        
        # Get response from agent
        response = agent.ask(prompt)
        
        # Hide thinking indicator
        socketio.emit('agent_thinking', {'thinking': False})
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in /api/ask endpoint: {str(e)}")
        socketio.emit('agent_thinking', {'thinking': False})
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500

@app.route('/api/switch_model', methods=['POST'])
def switch_model():
    """Switch to a specific model"""
    try:
        data = request.get_json()
        model_key = data.get('model_key')
        if not model_key:
            return jsonify({'error': 'No model key provided'}), 400

        result = agent.switch_model(model_key)
        return jsonify({'result': result})
    except Exception as e:
        print(f"Error in /api/switch_model endpoint: {str(e)}")
        return jsonify({'error': 'Failed to switch model', 'details': str(e)}), 500

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    """Clear conversation history"""
    try:
        agent.reset_history()
        return jsonify({'result': 'History cleared'})
    except Exception as e:
        print(f"Error in /api/clear_history endpoint: {str(e)}")
        return jsonify({'error': 'Failed to clear history', 'details': str(e)}), 500

@app.route('/api/cwd')
def get_cwd():
    """Get current working directory"""
    try:
        return jsonify({'cwd': os.getcwd()})
    except Exception as e:
        return jsonify({'error': 'Failed to get CWD', 'details': str(e)}), 500

@app.route('/api/shell', methods=['POST'])
def execute_shell():
    """Execute a shell command"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400

        # Security checks (copied from cli.py)
        dangerous_patterns = [
            'rm -rf', 'rm -r', 'rmdir', 'del /s', 'format', 'fdisk',
            'mkfs', 'dd if=', '>/dev/', '>/etc/',
            'cat > /etc/', 'echo > /etc/', 'chmod 777 /',
            'mv /etc/', 'cp /etc/', 'touch /etc/',
            'shutdown', 'reboot', 'poweroff', 'halt'
        ]

        cmd_lower = command.lower()
        for pattern in dangerous_patterns:
            if pattern in cmd_lower:
                return jsonify({'error': 'Command blocked for security reasons', 'output': f'Blocked potentially dangerous command: {command}'}), 403

        import subprocess
        
        # Additional injection checks
        injection_patterns = ['&&', '||', ';', '`', '$(', '|', '>', '>>', '<']
        for pattern in injection_patterns:
            if pattern in cmd_lower:
                 return jsonify({'error': 'Command blocked for security reasons (injection risk)', 'output': f'Blocked command with injection risk: {command}'}), 403

        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nError: {result.stderr}"
            
        return jsonify({
            'output': output,
            'returncode': result.returncode,
            'cwd': os.getcwd() # Return new CWD if it changed (though subprocess doesn't change parent CWD usually)
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timed out', 'output': 'Command execution timed out'}), 408
    except Exception as e:
        print(f"Error in /api/shell endpoint: {str(e)}")
        return jsonify({'error': 'Failed to execute command', 'details': str(e)}), 500

# Health check endpoint
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Codeius backend is running'})

def run_gui():
    """Starts the Flask server on port 8080."""
    import webbrowser
    from rich.console import Console
    from rich.table import Table
    import logging

    # Suppress Flask's default logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    port = 8080  # Fixed port
    local_url = f"http://localhost:{port}"
    network_url = f"http://{get_network_ip()}:{port}"

    # Create a rich console for better formatting
    console = Console()

    # Create a clean welcome message
    table = Table(show_header=True, header_style="bold magenta", border_style="blue")
    table.add_column("Type", style="cyan", justify="center")
    table.add_column("URL", style="green")

    table.add_row("Local", local_url)
    table.add_row("Network", network_url)

    console.print(table)
    console.print("[bold yellow]Press 'o' + Enter to open in browser, or Ctrl+C to exit[/bold yellow]")

    # Handle opening browser when 'o' is pressed
    import threading
    import sys

    browser_opened = [False]  # Use list to allow modification in nested function

    def check_input():
        while True:
            try:
                user_input = input().strip().lower()
                if user_input == 'o' and not browser_opened[0]:
                    browser_opened[0] = True
                    webbrowser.open(local_url)
                    console.print("\n[bold green]✓ Browser opened successfully![/bold green]")
                    console.print("[bold yellow]Press Ctrl+C to exit.[/bold yellow]")
                elif user_input in ['q', 'quit', 'exit']:
                    console.print("\n[bold red]Shutting down server...[/bold red]")
                    sys.exit(0)
            except (EOFError, KeyboardInterrupt):
                sys.exit(0)
            except Exception:
                pass  # Ignore other input errors

    # Start input thread
    input_thread = threading.Thread(target=check_input, daemon=True)
    input_thread.start()

    # Run the server with suppressed output
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False, log_output=False)


def get_network_ip():
    """Get the machine's network IP address"""
    import socket
    try:
        # Connect to a remote address to determine local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"


if __name__ == '__main__':
    run_gui()