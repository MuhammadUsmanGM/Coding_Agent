from codeius.core.plugin_system import BasePlugin
import datetime

class LoggerPlugin(BasePlugin):
    def __init__(self):
        super().__init__("LoggerPlugin", "1.0.0")
        
    def on_load(self):
        print("📝 Logger Plugin Loaded!")
        
    def on_message_received(self, message: str) -> str:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] User sent: {message[:50]}...")
        return message # Return unmodified

    def on_response_generated(self, response: str) -> str:
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] AI replied: {len(response)} chars")
        return response
