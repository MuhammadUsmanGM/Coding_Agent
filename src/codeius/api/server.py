# gui_server.py

import os
import socket
from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from src.coding_agent.agent import CodingAgent

app = Flask(__name__, static_folder='codeius-ui/build/static')
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")
agent = CodingAgent()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, '..', path)):
        return send_from_directory(os.path.join(app.static_folder, '..'), path)
    else:
        return send_from_directory(os.path.join(app.static_folder, '..'), 'index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400

    socketio.emit('agent_thinking', {'thinking': True})
    response = agent.ask(prompt)
    socketio.emit('agent_thinking', {'thinking': False})

    return jsonify({'response': response})

@app.route('/history')
def history():
    return jsonify({'history': agent.conversation_manager.get_conversation_context()})

def run_gui():
    """Starts the Flask server on an available port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()

    print(f"Starting GUI on http://localhost:{port}")
    socketio.run(app, port=port)

if __name__ == '__main__':
    run_gui()
