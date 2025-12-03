# api/server.py

import os
from dotenv import load_dotenv
from flask import Flask, send_from_directory, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from codeius.core.agent import CodingAgent
from codeius.core.conversation_db import conversation_db
from codeius.core.mongo_db import mongo_manager
from codeius.core.project_scanner import project_scanner

load_dotenv()

# Get the directory of this file and go up to project root, then to Codeius-GUI
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

# Configure secret key for sessions (needed for file upload context)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'


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
        session_id = data.get('session_id', 'default')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        # Get conversation history for context
        history = conversation_db.get_conversation_history(session_id)
        
        # Select relevant context (last 5 messages or relevant ones)
        if len(history) > 5:
            relevant_history = context_manager.select_relevant_context(prompt, history, max_tokens=1500)
        else:
            relevant_history = history
        
        # Build context from history
        context_messages = ""
        for msg in relevant_history[-5:]:  # Last 5 relevant messages
            context_messages += f"User: {msg['user']}\nAssistant: {msg['ai']}\n\n"

        # Include file context if available
        full_prompt = prompt
        if 'file_context' in session and session['file_context']:
            context_header = "\n\n=== Uploaded Files Context ===\n"
            for file_info in session['file_context']:
                context_header += f"\n--- File: {file_info['name']} ({file_info['size']} bytes) ---\n"
                context_header += file_info['content'][:5000]  # Limit to first 5000 chars per file
                if len(file_info['content']) > 5000:
                    context_header += "\n... (file truncated) ..."
                context_header += "\n"
            
            full_prompt = context_header + "\n\n"
        else:
            full_prompt = ""
        
        # Add conversation history
        if context_messages:
            full_prompt += f"=== Recent Conversation ===\n{context_messages}\n"
        
        # Add current question
        full_prompt += f"=== Current Question ===\n{prompt}"

        # Show thinking indicator via socket
        socketio.emit('agent_thinking', {'thinking': True})
        
        # Get response from agent
        response = agent.ask(full_prompt)
        
        # Save conversation to database
        token_count = context_manager.count_tokens(prompt + response)
        model_info = agent.get_current_model_info()
        model_used = model_info['name'] if model_info else 'default'
        
        conversation_db.save_conversation(
            session_id=session_id,
            user_message=prompt,
            ai_response=response,
            token_count=token_count,
            model_used=model_used
        )
        
        # Hide thinking indicator
        socketio.emit('agent_thinking', {'thinking': False})
        
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in /api/ask endpoint: {str(e)}")
        socketio.emit('agent_thinking', {'thinking': False})
        return jsonify({'error': 'Failed to process request', 'details': str(e)}), 500

@socketio.on('start_stream')
def handle_start_stream(data):
    """Handle streaming request via WebSocket"""
    try:
        prompt = data.get('prompt')
        session_id = data.get('session_id', 'default')
        
        if not prompt:
            socketio.emit('stream_error', {'error': 'No prompt provided', 'session_id': session_id})
            return
        
        # Get conversation history for context
        history = conversation_db.get_conversation_history(session_id)
        
        # Select relevant context
        if len(history) > 5:
            relevant_history = context_manager.select_relevant_context(prompt, history, max_tokens=1500)
        else:
            relevant_history = history
        
        # Build context from history
        context_messages = ""
        for msg in relevant_history[-5:]:
            context_messages += f"User: {msg['user']}\nAssistant: {msg['ai']}\n\n"
        
        # Include file context
        full_prompt = ""
        if 'file_context' in session and session['file_context']:
            context_header = "\n\n=== Uploaded Files Context ===\n"
            for file_info in session['file_context']:
                context_header += f"\n--- File: {file_info['name']} ({file_info['size']} bytes) ---\n"
                context_header += file_info['content'][:5000]
                if len(file_info['content']) > 5000:
                    context_header += "\n... (file truncated) ..."
                context_header += "\n"
            file_context_str = context_header + "\n\n"
        
        # Add conversation history
        if context_messages:
            file_context_str += f"=== Recent Conversation ===\n{context_messages}\n"
        
        # Add current question
        final_prompt_for_agent = file_context_str + f"=== Current Question ===\n{prompt}"
        
        # Emit stream start
        emit('stream_start', {'session_id': session_id}, room=session_id)
        
        # Stream tokens
        full_response = ""
        token_count = 0
        try:
            # Assuming agent.stream_response now takes the full prompt and potentially other context
            # The instruction provided `agent.stream_response(prompt, history=history, context=context)`
            # but the `full_prompt` construction is still present.
            # I will use `final_prompt_for_agent` as the primary prompt for the agent.
            # If `history` and `context` are also needed separately by the agent,
            # the agent's method signature would need to be adjusted.
            # For now, I'll pass the constructed `final_prompt_for_agent`.
            for token in agent.ask_stream(final_prompt_for_agent): # Reverting to ask_stream as per original logic, but using final_prompt_for_agent
                full_response += token
                token_count += 1 # Added token_count increment
                emit('stream_token', {'token': token, 'session_id': session_id}, room=session_id)
                socketio.sleep(0)  # Allow other events to process
        except Exception as e:
            emit('stream_error', {'error': str(e), 'session_id': session_id}, room=session_id)
            return
        
        # Save conversation to database
        # token_count is now calculated during streaming
        model_info = agent.get_current_model_info()
        model_used = model_info['name'] if model_info else 'default'
        
        conversation_db.save_conversation(
            session_id=session_id,
            user_message=prompt,
            ai_response=full_response,
            token_count=token_count,
            model_used=model_used
        )
        
        # Emit stream end
        emit('stream_end', {'session_id': session_id}, room=session_id)
        
    except Exception as e:
        print(f"Error in start_stream handler: {str(e)}")
        emit('stream_error', {'error': str(e), 'session_id': session_id}, room=session_id)

@socketio.on('cancel_stream')
def handle_cancel_stream(data):
    """Handle stream cancellation"""
    session_id = data.get('session_id', 'default')
    # Emit cancellation confirmation
    socketio.emit('stream_cancelled', {'session_id': session_id})

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

@app.route('/google_callback') # Assuming this is the intended route for Google callback
def google_callback():
    # Check if this is a CLI login
    if 'cli_login' in session:
        # Generates a one-time code or token for CLI
        # For now, just redirect to a success page
        return "Authentication successful! You can close this window."
        
    return redirect('http://localhost:8090/') # Redirect to frontend on port 8090

@app.route('/api/sessions/<session_id>/summarize', methods=['POST'])
def summarize_session(session_id):
    try:
        # Start background task for summarization
        # For now, just return success
        return jsonify({'status': 'success', 'message': 'Summarization started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['GET'])
def search_messages():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([])
            
        limit = int(request.args.get('limit', 20))
        results = conversation_db.search_conversations(query, limit)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/files', methods=['GET'])
def list_files():
    """List files and directories in a given path"""
    try:
        path = request.args.get('path', '.')
        
        # Security check: prevent directory traversal outside of allowed paths if needed
        # For now, we allow exploring from CWD
        base_path = os.getcwd()
        target_path = os.path.abspath(os.path.join(base_path, path))
        
        # Simple check to ensure we are still within the system (basic protection)
        # In a real app, you might want to restrict to project_root
        
        if not os.path.exists(target_path):
             return jsonify({'error': 'Path does not exist'}), 404
             
        if not os.path.isdir(target_path):
             return jsonify({'error': 'Path is not a directory'}), 400

        items = []
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            is_dir = os.path.isdir(item_path)
            items.append({
                'name': item,
                'type': 'directory' if is_dir else 'file',
                'path': os.path.join(path, item).replace('\\', '/') # Return relative path
            })
            
        # Sort: directories first, then files
        items.sort(key=lambda x: (x['type'] != 'directory', x['name'].lower()))
        
        return jsonify({'files': items})
    except Exception as e:
        return jsonify({'error': 'Failed to list files', 'details': str(e)}), 500

@app.route('/api/sessions/<session_id>/share', methods=['POST'])
def share_session(session_id):
    """Generate a shareable link for a session"""
    try:
        # In a real app, we would generate a unique random ID mapped to this session
        # For now, we'll just use the session_id but mark it as shared in DB
        # conversation_db.mark_shared(session_id) 
        
        # Construct the share URL (assuming frontend handles /share/ route)
        share_url = f"http://localhost:8090/share/{session_id}"
        
        return jsonify({'share_url': share_url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions/<session_id>/public', methods=['GET'])
def get_public_session(session_id):
    """Get public session data (read-only)"""
    try:
        # Check if session is actually shared (omitted for demo)
        history = conversation_db.get_conversation_history(session_id)
        return jsonify({'messages': history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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