"""
Plugin System for the Coding Agent
Allows users to extend functionality by dropping in their own Python scripts
"""
import os
import sys
import importlib.util
import inspect
from pathlib import Path
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
import json
from datetime import datetime


@dataclass
class PluginInfo:
    """Information about a loaded plugin"""
    name: str
    description: str
    version: str
    author: str
    capabilities: List[str]
    path: str
    loaded_at: datetime


class PluginManager:
    """Manages loading and executing user plugins"""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins_dir.mkdir(exist_ok=True)
        self.loaded_plugins: Dict[str, Any] = {}
        self.plugin_info: Dict[str, PluginInfo] = {}
        
        # Default plugins directory structure
        self._ensure_plugins_structure()
    
    def _ensure_plugins_structure(self):
        """Ensure the plugins directory structure exists"""
        (self.plugins_dir / "functions").mkdir(exist_ok=True)
        (self.plugins_dir / "tools").mkdir(exist_ok=True)
        (self.plugins_dir / "utils").mkdir(exist_ok=True)
    
    def load_plugins(self):
        """Load all available plugins from the plugins directory"""
        plugins_loaded = 0
        
        # Look for Python files in all subdirectories
        for py_file in self.plugins_dir.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue  # Skip special files like __init__.py
            
            plugin_name = py_file.stem
            try:
                plugin = self._load_plugin(str(py_file))
                if plugin:
                    self.loaded_plugins[plugin_name] = plugin
                    plugins_loaded += 1
                    # print(f"Loaded plugin: {plugin_name}")  # Keep interface clean
            except Exception as e:
                # print(f"Failed to load plugin {plugin_name}: {e}")  # Keep interface clean
                pass  # Silently handle plugin load errors to keep interface clean
        
        if plugins_loaded > 0 or True:  # Always show even if 0 for consistency
            print(f"Total plugins loaded: {plugins_loaded}")
    
    def _load_plugin(self, plugin_path: str):
        """Load a single plugin from the given path"""
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        if spec is None or spec.loader is None:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Look for callable functions in the module
        plugin_functions = {}
        for name, obj in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith('_'):  # Skip private functions
                plugin_functions[name] = obj
        
        return plugin_functions if plugin_functions else None
    
    def execute_plugin(self, plugin_name: str, function_name: str, *args, **kwargs):
        """Execute a specific function from a plugin"""
        if plugin_name not in self.loaded_plugins:
            raise ValueError(f"Plugin '{plugin_name}' not loaded")
        
        plugin = self.loaded_plugins[plugin_name]
        if function_name not in plugin:
            raise ValueError(f"Function '{function_name}' not found in plugin '{plugin_name}'")
        
        return plugin[function_name](*args, **kwargs)
    
    def get_available_plugins(self) -> Dict[str, List[str]]:
        """Get a list of available plugins and their functions"""
        result = {}
        for plugin_name, plugin in self.loaded_plugins.items():
            result[plugin_name] = list(plugin.keys())
        return result
    
    def create_plugin_skeleton(self, name: str, description: str = "", author: str = "", version: str = "1.0.50"):
        """Create a skeleton for a new plugin"""
        plugin_content = f'''"""
{name} Plugin
{description}
Author: {author}
Version: {version}
"""

def example_function(input_data):
    """
    Example function demonstrating plugin structure
    """
    # Your plugin logic here
    result = f"Processed: {{input_data}}"
    return result

# Add more functions as needed for your plugin
'''
        
        plugin_path = self.plugins_dir / f"{name}.py"
        with open(plugin_path, 'w', encoding='utf-8') as f:
            f.write(plugin_content)
        
        return str(plugin_path)


# Global plugin manager instance
plugin_manager = PluginManager()