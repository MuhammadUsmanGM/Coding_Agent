"""
Model management service for the CodingAgent.
Separates the model switching and management logic from the main agent class.
"""
from typing import Dict, Any, Optional
from coding_agent.provider.multiprovider import MultiProvider
from coding_agent.provider.groq import GroqProvider
from coding_agent.provider.google import GoogleProvider
from coding_agent.provider.mcp import MCPProvider
from coding_agent.mcp_manager import mcp_manager


class ModelManager:
    """Handles model switching and management."""
    
    def __init__(self):
        # Initialize MCP server manager
        self.mcp_manager = mcp_manager

        # Initialize providers including cloud providers and MCP servers
        self.providers = [GroqProvider(), GoogleProvider()]

        # Add MCP server providers
        mcp_servers = self.mcp_manager.list_servers()
        for server in mcp_servers:
            if server.enabled:
                self.providers.append(MCPProvider(server.name))

        self.llm = MultiProvider(self.providers)
        
    def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active provider/model"""
        if hasattr(self.llm, 'current') and hasattr(self.llm, 'providers'):
            current_idx = self.llm.current
            if 0 <= current_idx < len(self.providers):
                provider = self.providers[current_idx]
                model_name = getattr(provider, 'model', 'unknown')
                provider_name = type(provider).__name__.replace('Provider', '')
                return {
                    'index': current_idx,
                    'name': model_name,
                    'provider': provider_name,
                    'key': f"{provider_name.lower()}_{current_idx}"
                }
        return None

    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available AI models only (excluding MCP tools)"""
        models: Dict[str, Any] = {}
        for i, provider in enumerate(self.providers):
            # Extract model information from each provider
            provider_type = type(provider)

            if provider_type.__name__ != 'MCPProvider':
                # Only include non-MCP providers (actual AI models)
                model_name = getattr(provider, 'model', 'unknown')
                provider_name = provider_type.__name__.replace('Provider', '')
                provider_type_str = 'cloud' if provider_name in ['Groq', 'Google'] else 'other'
                models[f"{provider_name.lower()}_{i}"] = {
                    'name': model_name,
                    'provider': provider_name,
                    'instance': provider,
                    'type': provider_type_str
                }
        return models

    def get_available_mcp_tools(self) -> Dict[str, Any]:
        """Get list of available MCP tools/servers"""
        tools: Dict[str, Any] = {}
        for i, provider in enumerate(self.providers):
            provider_type = type(provider)

            if provider_type.__name__ == 'MCPProvider':
                # Handle MCP provider specifically
                server_name = getattr(provider, 'server_name', 'mcp_server')
                provider_name = 'mcp'
                tools[f"mcp_{i}"] = {
                    'name': server_name,
                    'provider': provider_name,
                    'instance': provider,
                    'type': 'mcp'
                }
        return tools

    def switch_model(self, model_key: str) -> str:
        """Switch to a specific model by key"""
        models = self.get_available_models()
        if model_key in models:
            # Find the provider index corresponding to the model key
            for i, provider in enumerate(self.providers):
                provider_name = type(provider).__name__.replace('Provider', '')
                current_key = f"{provider_name.lower()}_{i}"
                if current_key == model_key:
                    # Set the specific provider in the MultiProvider
                    self.llm.set_provider(i)
                    return f"Switched to {models[model_key]['name']} ({models[model_key]['provider']})"
        return f"Model {model_key} not found. Use /models to see available models."
        
    def chat(self, messages: list, max_tokens: int = 2048):
        """Call the LLM with the provided messages."""
        return self.llm.chat(messages, max_tokens)