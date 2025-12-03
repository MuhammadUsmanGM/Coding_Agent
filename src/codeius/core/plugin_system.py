import os
import importlib.util
import inspect
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """Base class for all Codeius plugins"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True

    @abstractmethod
    def on_load(self):
        """Called when the plugin is loaded"""
        pass

    def on_message_received(self, message: str) -> Optional[str]:
        """Called when a user message is received. Return modified message or None."""
        return None

    def on_response_generated(self, response: str) -> Optional[str]:
        """Called when an AI response is generated. Return modified response or None."""
        return None

    def on_tool_call(self, tool_name: str, args: Dict) -> None:
        """Called when a tool is executed"""
        pass

    def on_shutdown(self):
        """Called when the application shuts down"""
        pass


class PluginManager:
    """Manages plugin discovery, loading, and hook execution"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, BasePlugin] = {}
        self.hooks = {
            'on_message_received': [],
            'on_response_generated': [],
            'on_tool_call': [],
            'on_shutdown': []
        }
        
        # Ensure plugin directory exists
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)

    def discover_plugins(self):
        """Scan plugin directory for python files"""
        if not os.path.exists(self.plugin_dir):
            return

        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                self.load_plugin(os.path.join(self.plugin_dir, filename))

    def load_plugin(self, filepath: str):
        """Load a plugin from a file"""
        try:
            module_name = os.path.basename(filepath)[:-3]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if not spec or not spec.loader:
                return
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find BasePlugin subclasses
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj is not BasePlugin):
                    
                    # Instantiate and register
                    plugin = obj()
                    self.register_plugin(plugin)
                    print(f"Loaded plugin: {plugin.name} v{plugin.version}")
                    
        except Exception as e:
            print(f"Failed to load plugin {filepath}: {str(e)}")

    def register_plugin(self, plugin: BasePlugin):
        """Register a plugin instance"""
        self.plugins[plugin.name] = plugin
        plugin.on_load()

    def run_hook(self, hook_name: str, *args, **kwargs) -> Any:
        """Run a hook across all enabled plugins"""
        result = None
        
        for plugin in self.plugins.values():
            if not plugin.enabled:
                continue
                
            if hasattr(plugin, hook_name):
                method = getattr(plugin, hook_name)
                try:
                    # For hooks that return modified data (chaining)
                    if hook_name in ['on_message_received', 'on_response_generated']:
                        # Use previous result as input if available, else first arg
                        current_input = result if result is not None else args[0]
                        hook_result = method(current_input)
                        if hook_result is not None:
                            result = hook_result
                    else:
                        # Just execute for side effects
                        method(*args, **kwargs)
                        
                except Exception as e:
                    print(f"Error in plugin {plugin.name} hook {hook_name}: {str(e)}")
                    
        return result if result is not None else (args[0] if args else None)

# Singleton instance
plugin_manager = PluginManager()
