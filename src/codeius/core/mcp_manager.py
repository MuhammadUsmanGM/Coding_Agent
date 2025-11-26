"""
MCP (Model Context Protocol) Server Manager for connecting to various model providers
"""
import asyncio
import json
from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel
from contextlib import asynccontextmanager
import subprocess
import os


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server"""
    name: str
    description: str
    endpoint: str
    enabled: bool = True
    capabilities: List[str] = []  # e.g., ["text-generation", "code-completion"]


class MCPServerManager:
    """Manager for MCP servers that can provide access to various tools and services"""
    
    def __init__(self, settings_path: str = "settings.json"):
        self.servers: Dict[str, MCPServerConfig] = {}
        self.settings_path = settings_path
        self._initialize_servers_from_settings()
    
    def _initialize_servers_from_settings(self):
        """Initialize servers based on settings configuration"""
        # Load settings from the settings.json file
        settings = self._load_settings()
        
        if "mcp_servers" in settings:
            for server_name, server_config in settings["mcp_servers"].items():
                if server_config.get("enabled", True):
                    self.servers[server_name] = MCPServerConfig(
                        name=server_name,
                        description=f"Server for {server_name.replace('-', ' ')}",
                        endpoint=server_config.get("endpoint", f"http://localhost:8000"),
                        enabled=server_config.get("enabled", True),
                        capabilities=server_config.get("capabilities", [])
                    )
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from the settings file"""
        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Settings file {self.settings_path} not found. Using defaults.")
            # Return default configuration
            return {
                "mcp_servers": {
                    "code-runner": {
                        "enabled": True,
                        "endpoint": "http://localhost:9000",
                        "capabilities": ["code-execution", "python"]
                    },
                    "filesystem": {
                        "enabled": True,
                        "endpoint": "http://localhost:9100",
                        "capabilities": ["file-operations", "read-files", "list-files"]
                    },
                    "duckduckgo": {
                        "enabled": True,
                        "endpoint": "http://localhost:9200",
                        "capabilities": ["web-search", "search"]
                    },
                    "code-search": {
                        "enabled": True,
                        "endpoint": "http://localhost:9300",
                        "capabilities": ["code-search", "function", "class", "todo"]
                    },
                    "shell": {
                        "enabled": True,
                        "endpoint": "http://localhost:9400",
                        "capabilities": ["shell", "command-execution"]
                    },
                    "testing": {
                        "enabled": True,
                        "endpoint": "http://localhost:9500",
                        "capabilities": ["testing", "pytest", "unittest"]
                    },
                    "doc-search": {
                        "enabled": True,
                        "endpoint": "http://localhost:9600",
                        "capabilities": ["doc-search", "md-search", "documentation"]
                    },
                    "database": {
                        "enabled": True,
                        "endpoint": "http://localhost:9700",
                        "capabilities": ["sql", "sqlite", "database"]
                    },
                    "ocr": {
                        "enabled": True,
                        "endpoint": "http://localhost:9800",
                        "capabilities": ["ocr", "image-processing", "text-extraction"]
                    },
                    "refactor": {
                        "enabled": True,
                        "endpoint": "http://localhost:9900",
                        "capabilities": ["refactoring", "code-quality", "analysis"]
                    },
                    "diff": {
                        "enabled": True,
                        "endpoint": "http://localhost:10000",
                        "capabilities": ["diff", "comparison", "file-comparison"]
                    }
                }
            }
    
    def list_servers(self) -> List[MCPServerConfig]:
        """List all available MCP servers"""
        return list(self.servers.values())
    
    def add_server(self, config: MCPServerConfig) -> bool:
        """Add a new MCP server"""
        self.servers[config.name] = config
        return True
    
    def remove_server(self, name: str) -> bool:
        """Remove an MCP server"""
        if name in self.servers:
            del self.servers[name]
            return True
        return False
    
    def enable_server(self, name: str) -> bool:
        """Enable an MCP server"""
        if name in self.servers:
            self.servers[name].enabled = True
            return True
        return False
    
    def disable_server(self, name: str) -> bool:
        """Disable an MCP server"""
        if name in self.servers:
            self.servers[name].enabled = False
            return True
        return False
    
    async def query_server(self, server_name: str, messages: List[Dict[str, str]], max_tokens: int = 2048) -> str:
        """Query an MCP server (simulated implementation)"""
        if server_name not in self.servers:
            raise ValueError(f"Server {server_name} not registered")
        
        server = self.servers[server_name]
        if not server.enabled:
            raise ValueError(f"Server {server_name} is not enabled")
        
        # In a real implementation, this would make an actual call to the MCP server
        # For now, we'll simulate a response
        user_message = messages[-1]["content"] if messages else "Hello"
        
        # Simulate a response based on the server and user message
        simulated_response = f"I'm the {server.name} server. Based on your request: {user_message[:100]}..."
        
        return simulated_response


@asynccontextmanager
async def lifespan(app):
    """Lifespan manager for the MCP server manager"""
    # Initialization code here
    yield
    # Cleanup code here


# Global instance of the MCP server manager
mcp_manager = MCPServerManager()