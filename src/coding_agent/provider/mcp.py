"""
MCP (Model Context Protocol) Provider for the Coding Agent
"""
import requests
from typing import Optional, List, Dict, Any
from coding_agent.provider.base import ProviderBase
from coding_agent.mcp_manager import mcp_manager


class MCPProvider(ProviderBase):
    """
    Provider that connects to MCP servers for various capabilities
    """
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.mcp_manager = mcp_manager
        self._setup_server_connection()
    
    def _setup_server_connection(self):
        """Get server configuration from the manager"""
        if self.server_name in self.mcp_manager.servers:
            self.server_config = self.mcp_manager.servers[self.server_name]
        else:
            raise ValueError(f"Server {self.server_name} not found in MCP manager")
    
    def chat(self, messages, max_tokens=2048):
        """
        Interact with the appropriate MCP server based on its function
        """
        try:
            if self.server_name == "code-runner":
                return self._run_code_server(messages)
            elif self.server_name == "filesystem":
                return self._filesystem_server(messages)
            elif self.server_name == "duckduckgo":
                return self._search_server(messages)
            else:
                return self._default_server_interaction(messages)
        except Exception as e:
            return f"Error communicating with {self.server_name} server: {str(e)}"
    
    def _run_code_server(self, messages):
        """Handle code execution requests"""
        # Extract the code from the last message
        last_message = messages[-1]["content"] if messages else ""
        
        # Simple heuristic to detect if this is a code execution request
        if "run" in last_message.lower() or "execute" in last_message.lower() or "python" in last_message.lower():
            # Extract the code to run - this is a simplified approach
            # In a real implementation, the LLM would structure these requests properly
            import re
            code_match = re.search(r'```python\n(.*?)\n```', last_message, re.DOTALL)
            if code_match:
                code = code_match.group(1)
                
                # Make request to code runner server
                response = requests.post(
                    f"{self.server_config.endpoint}/run_code",
                    json={"code": code},
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    output = result.get("stdout", "") or result.get("stderr", "No output")
                    return f"Code execution result:\n{output}"
                else:
                    return f"Error running code: {response.status_code} - {response.text}"
            else:
                return "No Python code block found to execute."
        else:
            return f"Code runner server received: {last_message[:100]}..."
    
    def _filesystem_server(self, messages):
        """Handle file system requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Check if this is a file request
        if "list" in last_message.lower() and "file" in last_message.lower():
            # Request file listing
            response = requests.get(f"{self.server_config.endpoint}/list_files")
            if response.status_code == 200:
                files = response.json()
                return f"Files in workspace:\n" + "\n".join(files)
            else:
                return f"Error listing files: {response.status_code} - {response.text}"
        elif "read" in last_message.lower() and "file" in last_message.lower():
            # Extract filename - simplified parsing
            import re
            filename_match = re.search(r'"([^"]*)"', last_message) or re.search(r"'([^']*)'", last_message)
            if filename_match:
                filename = filename_match.group(1)
                response = requests.get(f"{self.server_config.endpoint}/read_file?fname={filename}")
                if response.status_code == 200:
                    return f"Content of {filename}:\n{response.text}"
                else:
                    return f"Error reading file {filename}: {response.status_code} - {response.text}"
            else:
                return "Could not identify filename to read."
        else:
            return f"File system server received: {last_message[:100]}..."
    
    def _search_server(self, messages):
        """Handle search requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Extract search query - simplified approach
        if any(word in last_message.lower() for word in ["search", "find", "look up", "google", "web"]):
            # Simple approach to extract search query
            query = last_message.split("search", 1)[-1].split("for", 1)[-1].strip() if "search" in last_message.lower() else last_message
            query = query.split("find", 1)[-1].strip() if "find" in last_message.lower() else query
            
            response = requests.get(f"{self.server_config.endpoint}/search?q={query}")
            if response.status_code == 200:
                results = response.json()
                return f"Search results for '{query}':\n{results.get('results', 'No results found')[:500]}..."
            else:
                return f"Error with search: {response.status_code} - {response.text}"
        else:
            return f"Search server received: {last_message[:100]}..."
    
    def _default_server_interaction(self, messages):
        """Default interaction for other server types"""
        last_message = messages[-1]["content"] if messages else ""
        return f"Server {self.server_name} received: {last_message[:100]}..."