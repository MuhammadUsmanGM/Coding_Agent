"""
Configuration Management System for Codeius AI Coding Agent

This module handles all configuration settings for the application.
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class AgentConfig:
    """Configuration settings for the AI agent."""
    # LLM Settings
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    google_api_key: str = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    groq_model: str = os.getenv("GROQ_API_MODEL", "llama3-70b-8192")
    google_model: str = os.getenv("GOOGLE_API_MODEL", "gemini-1.5-flash")
    
    # Performance Settings
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2048"))
    conversation_history_limit: int = int(os.getenv("CONVERSATION_HISTORY_LIMIT", "50"))
    
    # File Operation Settings
    allowed_extensions: set = field(default_factory=lambda: {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css',
        '.json', '.txt', '.md', '.yaml', '.yml', '.xml', '.ini',
        '.cfg', '.conf', '.env', '.sql', '.pyi'
    })
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    
    # Security Settings
    max_concurrent_operations: int = int(os.getenv("MAX_CONCURRENT_OPERATIONS", "5"))
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    
    # MCP Server Settings
    mcp_server_timeout: int = int(os.getenv("MCP_SERVER_TIMEOUT", "30"))
    mcp_server_retry_attempts: int = int(os.getenv("MCP_SERVER_RETRY_ATTEMPTS", "3"))
    
    # Workspace Settings
    workspace_root: str = os.getenv("WORKSPACE_ROOT", ".")
    
    def __post_init__(self):
        """Post-initialization validation."""
        if not self.groq_api_key and not self.google_api_key:
            print("⚠️ Warning: No API keys found. Please set GROQ_API_KEY or GOOGLE_API_KEY in environment variables.")
        if self.max_file_size_mb <= 0:
            self.max_file_size_mb = 10
        if self.conversation_history_limit <= 0:
            self.conversation_history_limit = 50

@dataclass
class UIConfig:
    """Configuration settings for the user interface."""
    # Color scheme
    primary_color: str = "#8A2BE2"  # Deep purple
    secondary_color: str = "#9370DB"  # Medium purple
    accent_color: str = "#7CFC00"  # Chartreuse green
    success_color: str = "#32CD32"  # Lime green
    error_color: str = "#FF4500"  # Orange red
    warning_color: str = "#FFA500"  # Orange
    
    # UI Settings
    show_startup_animation: bool = True
    startup_animation_dots: int = 3
    startup_animation_delay: float = 0.3
    show_system_status: bool = True
    show_conversation_summary: bool = True

@dataclass
class SecurityConfig:
    """Security-related configuration settings."""
    # Plugin security
    enable_plugin_sandbox: bool = False  # When true, plugins run in restricted environment
    max_plugin_execution_time: int = int(os.getenv("MAX_PLUGIN_EXECUTION_TIME", "30"))
    
    # API security
    enable_api_rate_limiting: bool = True
    enable_api_caching: bool = True
    
    # File operation security
    restrict_file_operations_to_workspace: bool = True
    validate_file_extensions: bool = True
    
    # Path traversal prevention
    enforce_canonical_paths: bool = True

class ConfigurationManager:
    """Manages application configuration."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/settings.json"
        self.agent_config = AgentConfig()
        self.ui_config = UIConfig()
        self.security_config = SecurityConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file if available."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Update agent config from file
                agent_data = data.get('agent', {})
                for key, value in agent_data.items():
                    if hasattr(self.agent_config, key):
                        setattr(self.agent_config, key, value)
                
                # Update UI config from file
                ui_data = data.get('ui', {})
                for key, value in ui_data.items():
                    if hasattr(self.ui_config, key):
                        setattr(self.ui_config, key, value)
                
                # Update security config from file
                security_data = data.get('security', {})
                for key, value in security_data.items():
                    if hasattr(self.security_config, key):
                        setattr(self.security_config, key, value)
                        
        except Exception as e:
            print(f"⚠️ Warning: Could not load config from {self.config_file}: {e}")
    
    def save_config(self):
        """Save current configuration to file."""
        config_dir = Path(self.config_file).parent
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            'agent': {
                'groq_model': self.agent_config.groq_model,
                'google_model': self.agent_config.google_model,
                'max_tokens': self.agent_config.max_tokens,
                'conversation_history_limit': self.agent_config.conversation_history_limit,
                'max_file_size_mb': self.agent_config.max_file_size_mb,
                'max_concurrent_operations': self.agent_config.max_concurrent_operations,
                'rate_limit_requests': self.agent_config.rate_limit_requests,
                'rate_limit_window_seconds': self.agent_config.rate_limit_window_seconds,
                'mcp_server_timeout': self.agent_config.mcp_server_timeout,
                'mcp_server_retry_attempts': self.agent_config.mcp_server_retry_attempts,
                'workspace_root': self.agent_config.workspace_root,
            },
            'ui': {
                'primary_color': self.ui_config.primary_color,
                'secondary_color': self.ui_config.secondary_color,
                'accent_color': self.ui_config.accent_color,
                'success_color': self.ui_config.success_color,
                'error_color': self.ui_config.error_color,
                'warning_color': self.ui_config.warning_color,
                'show_startup_animation': self.ui_config.show_startup_animation,
                'startup_animation_dots': self.ui_config.startup_animation_dots,
                'startup_animation_delay': self.ui_config.startup_animation_delay,
                'show_system_status': self.ui_config.show_system_status,
                'show_conversation_summary': self.ui_config.show_conversation_summary,
            },
            'security': {
                'enable_plugin_sandbox': self.security_config.enable_plugin_sandbox,
                'max_plugin_execution_time': self.security_config.max_plugin_execution_time,
                'enable_api_rate_limiting': self.security_config.enable_api_rate_limiting,
                'enable_api_caching': self.security_config.enable_api_caching,
                'restrict_file_operations_to_workspace': self.security_config.restrict_file_operations_to_workspace,
                'validate_file_extensions': self.security_config.validate_file_extensions,
                'enforce_canonical_paths': self.security_config.enforce_canonical_paths,
            }
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2)
    
    def get_agent_config(self) -> AgentConfig:
        """Get the agent configuration."""
        return self.agent_config
    
    def get_ui_config(self) -> UIConfig:
        """Get the UI configuration."""
        return self.ui_config
    
    def get_security_config(self) -> SecurityConfig:
        """Get the security configuration."""
        return self.security_config

# Global configuration instance
config_manager = ConfigurationManager()