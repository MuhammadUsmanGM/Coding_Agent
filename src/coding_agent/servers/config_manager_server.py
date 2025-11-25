"""
Advanced Configuration/Settings Tool
Interactive config/credentials manager for .env, YAML, or TOML settings—all changes local and secure.
"""
from flask import Flask, request, jsonify
import os
import json
import yaml
import toml
from pathlib import Path
import re

app = Flask(__name__)

class ConfigManager:
    def __init__(self, config_dir="config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        # Paths to common config files
        self.common_configs = {
            "env": self.config_dir / ".env",
            "yaml": self.config_dir / "config.yaml",
            "yml": self.config_dir / "config.yml",
            "toml": self.config_dir / "config.toml",
            "json": self.config_dir / "config.json"
        }
    
    def read_config(self, config_type="env"):
        """Read configuration from the specified file type"""
        try:
            if config_type == "env":
                file_path = self.common_configs["env"]
                if not file_path.exists():
                    # Create a default .env file
                    with open(file_path, 'w') as f:
                        f.write("# Environment variables configuration\n")
                        f.write("# Add your settings below\n")
                    return {}
                
                config = {}
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
                return config
            
            elif config_type in ["yaml", "yml"]:
                file_path = self.common_configs[config_type]
                if not file_path.exists():
                    # Create a default YAML file
                    with open(file_path, 'w') as f:
                        yaml.dump({}, f)
                    return {}
                
                with open(file_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            
            elif config_type == "toml":
                file_path = self.common_configs["toml"]
                if not file_path.exists():
                    # Create a default TOML file
                    with open(file_path, 'w') as f:
                        toml.dump({}, f)
                    return {}
                
                with open(file_path, 'r') as f:
                    return toml.load(f)
            
            elif config_type == "json":
                file_path = self.common_configs["json"]
                if not file_path.exists():
                    # Create a default JSON file
                    with open(file_path, 'w') as f:
                        json.dump({}, f, indent=2)
                    return {}
                
                with open(file_path, 'r') as f:
                    return json.load(f)
        
        except Exception as e:
            return {"error": str(e)}
    
    def write_config(self, config_data, config_type="env"):
        """Write configuration to the specified file type"""
        try:
            if config_type == "env":
                file_path = self.common_configs["env"]
                with open(file_path, 'w') as f:
                    f.write("# Environment variables configuration\n")
                    for key, value in config_data.items():
                        f.write(f"{key}={value}\n")
                return {"status": "success", "message": f"Environment variables saved to {file_path}"}
            
            elif config_type in ["yaml", "yml"]:
                file_path = self.common_configs[config_type]
                with open(file_path, 'w') as f:
                    yaml.dump(config_data, f, default_flow_style=False)
                return {"status": "success", "message": f"YAML configuration saved to {file_path}"}
            
            elif config_type == "toml":
                file_path = self.common_configs["toml"]
                with open(file_path, 'w') as f:
                    toml.dump(config_data, f)
                return {"status": "success", "message": f"TOML configuration saved to {file_path}"}
            
            elif config_type == "json":
                file_path = self.common_configs["json"]
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                return {"status": "success", "message": f"JSON configuration saved to {file_path}"}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_available_configs(self):
        """List all available config files"""
        configs = {}
        for config_type, file_path in self.common_configs.items():
            configs[config_type] = {
                "exists": file_path.exists(),
                "path": str(file_path),
                "size": file_path.stat().st_size if file_path.exists() else 0
            }
        return configs
    
    def update_setting(self, key, value, config_type="env"):
        """Update a specific setting in the configuration"""
        current_config = self.read_config(config_type)
        if "error" in current_config:
            return current_config
        
        current_config[key] = value
        return self.write_config(current_config, config_type)

config_manager = ConfigManager()

@app.route('/config', methods=['GET', 'POST'])
def handle_config():
    """Handle configuration management requests"""
    try:
        action = request.json.get('action', 'view')
        config_type = request.json.get('config_type', 'env')
        key = request.json.get('key', None)
        value = request.json.get('value', None)
        
        if action == 'view' or action == 'read':
            config_data = config_manager.read_config(config_type)
            return jsonify({
                'success': True,
                'config_type': config_type,
                'data': config_data
            })
        
        elif action == 'save' or action == 'write':
            config_data = request.json.get('data', {})
            result = config_manager.write_config(config_data, config_type)
            if result.get('status') == 'success':
                return jsonify({
                    'success': True,
                    'message': result['message']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result['message']
                }), 400
        
        elif action == 'update' or action == 'set':
            if key is not None and value is not None:
                result = config_manager.update_setting(key, value, config_type)
                if result.get('status') == 'success':
                    return jsonify({
                        'success': True,
                        'message': result['message']
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result['message']
                    }), 400
            else:
                return jsonify({
                    'success': False,
                    'error': 'Key and value required for update action'
                }), 400
        
        elif action == 'list' or action == 'available':
            configs = config_manager.get_available_configs()
            return jsonify({
                'success': True,
                'configs': configs
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown action: {action}'
            }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=10700)