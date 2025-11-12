"""
MCP (Model Context Protocol) Provider for the Coding Agent
"""
from typing import Optional, List, Dict, Any
from coding_agent.provider.base import ProviderBase
from coding_agent.mcp_manager import mcp_manager


class MCPProvider(ProviderBase):
    """
    Provider that connects to MCP servers for model access
    """
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.mcp_manager = mcp_manager
        
    def chat(self, messages, max_tokens=2048):
        """
        Chat with the model via an MCP server
        """
        if self.mcp_manager:
            import asyncio
            import concurrent.futures
            
            # Use a thread pool to run the async method
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._sync_chat, messages, max_tokens)
                return future.result()
        else:
            return f"Error: MCP server {self.server_name} not available"
    
    def _sync_chat(self, messages, max_tokens):
        """
        Synchronous wrapper for the async chat method
        """
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.mcp_manager.query_server(self.server_name, messages, max_tokens)
            )
        finally:
            loop.close()