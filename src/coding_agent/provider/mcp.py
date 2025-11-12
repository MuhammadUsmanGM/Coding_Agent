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
            elif self.server_name == "code-search":
                return self._code_search_server(messages)
            elif self.server_name == "shell":
                return self._shell_server(messages)
            elif self.server_name == "testing":
                return self._testing_server(messages)
            elif self.server_name == "doc-search":
                return self._doc_search_server(messages)
            elif self.server_name == "database":
                return self._database_server(messages)
            elif self.server_name == "ocr":
                return self._ocr_server(messages)
            elif self.server_name == "refactor":
                return self._refactor_server(messages)
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
    
    def _code_search_server(self, messages):
        """Handle code search requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Determine what to search for
        search_type = "function"  # default
        if "class" in last_message.lower():
            search_type = "class"
        elif "todo" in last_message.lower() or "TODO" in last_message:
            search_type = "todo"
        
        # Make request to code search server
        import os
        project_root = os.getcwd()  # Use current working directory as project root
        search_url = f"{self.server_config.endpoint}/search?type={search_type}&root={project_root}"
        
        try:
            response = requests.get(search_url)
            if response.status_code == 200:
                results = response.json()
                if results:
                    output = f"Found {len(results)} {search_type}(s) in project:\n"
                    for result in results[:10]:  # Limit to first 10 results
                        output += f"  {result['file']}:{result['line']} - {result['match']}\n"
                    return output
                else:
                    return f"No {search_type}s found in project."
            else:
                return f"Error with code search: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error performing code search: {str(e)}"
    
    def _shell_server(self, messages):
        """Handle shell command requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # For now, we'll implement a simple shell command execution
        # The message should contain the command to execute
        if "run" in last_message.lower() and "|" in last_message:
            # Extract command after a pipe character, e.g., "please run | ls -la"
            parts = last_message.split("|", 1)
            if len(parts) > 1:
                command = parts[1].strip()
                
                try:
                    response = requests.post(
                        f"{self.server_config.endpoint}/shell",
                        json={"cmd": command},
                        timeout=30
                    )
                    if response.status_code == 200:
                        result = response.json()
                        output = result.get("stdout", "") or result.get("stderr", "No output")
                        if result.get("returncode", 0) != 0:
                            output = f"[Exit code {result.get('returncode', 0)}] " + output
                        return f"Command output:\n{output}"
                    else:
                        return f"Error running command: {response.status_code} - {response.text}"
                except Exception as e:
                    return f"Error executing shell command: {str(e)}"
        else:
            return f"Shell server received: {last_message[:100]}... (use format: 'run | <command>')"
    
    def _testing_server(self, messages):
        """Handle testing requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # For testing, we'll run the test suite when requested
        if any(word in last_message.lower() for word in ["test", "pytest", "run tests", "check"]):
            try:
                response = requests.post(
                    f"{self.server_config.endpoint}/test",
                    timeout=120  # 2 minute timeout for tests
                )
                if response.status_code == 200:
                    result = response.json()
                    output = result.get("stdout", "") or result.get("stderr", "No output")
                    return f"Test results:\n{output[:1000]}..."  # Limit output length
                else:
                    return f"Error running tests: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Error executing tests: {str(e)}"
        else:
            return f"Testing server received: {last_message[:100]}..."
    
    def _doc_search_server(self, messages):
        """Handle documentation search requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Extract search query - look for documentation-related keywords
        if any(word in last_message.lower() for word in ["doc", "documentation", "readme", "help", "how to", "guide"]):
            # Simple approach to extract search query
            query = last_message
            if "about" in last_message.lower():
                query = last_message.split("about", 1)[-1].strip()
            elif "for" in last_message.lower():
                query = last_message.split("for", 1)[-1].strip()
            
            import os
            docs_root = os.getcwd()  # Use current project as documentation root
            search_url = f"{self.server_config.endpoint}/doc_search?q={query}&root={docs_root}"
            
            try:
                response = requests.get(search_url)
                if response.status_code == 200:
                    results = response.json()
                    if results:
                        output = f"Found {len(results)} documentation matches:\n"
                        for result in results[:5]:  # Limit to first 5 results
                            output += f"  {result['file']}:{result['line']} - {result['match']}\n"
                        return output
                    else:
                        return f"No documentation matches found for '{query}'."
                else:
                    return f"Error with doc search: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Error performing doc search: {str(e)}"
        else:
            return f"Doc search server received: {last_message[:100]}..."
    
    def _database_server(self, messages):
        """Handle database query requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for SQL-related keywords in the message
        if any(word in last_message.lower() for word in ["select", "from", "where", "sql", "database", "query", "table"]):
            # For now, we'll simulate a simple query based on the message
            # In a real implementation, we'd need more sophisticated parsing
            sql_query = last_message[-500:]  # Take the last last 500 chars as potential query
            sql_query = sql_query.strip()
            if not sql_query.lower().startswith("select "):
                # If not explicitly a SELECT, we won't execute it for safety
                return f"Database server can only execute SELECT queries for safety. Received: {sql_query[:100]}..."
            
            try:
                response = requests.post(
                    f"{self.server_config.endpoint}/query",
                    json={"sql": sql_query},
                    timeout=30
                )
                if response.status_code == 200:
                    result = response.json()
                    if "error" in result:
                        return f"Database error: {result['error']}"
                    else:
                        rows = result.get("rows", [])
                        columns = result.get("columns", [])
                        if rows:
                            output = f"Query results ({len(rows)} rows):\n"
                            output += f"Columns: {', '.join(columns) if columns else 'N/A'}\n"
                            for row in rows[:10]:  # Limit to first 10 rows
                                output += f"  {row}\n"
                            return output
                        else:
                            return "Query executed successfully but returned no results."
                else:
                    return f"Error with database query: {response.status_code} - {response.text}"
            except Exception as e:
                return f"Error executing database query: {str(e)}"
        else:
            return f"Database server received: {last_message[:100]}... (waiting for SQL query)"
    
    def _ocr_server(self, messages):
        """Handle OCR requests for reading text from images"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest an OCR request
        if any(word in last_message.lower() for word in ["ocr", "image", "screenshot", "png", "jpg", "jpeg", "read from", "extract text"]):
            # This is a simplified implementation. In a real implementation, the agent would need
            # to send image data to the OCR server, but for now we'll just return a message
            # indicating what would happen.
            return f"OCR server would process image from: {last_message[:100]}..."
        else:
            return f"OCR server received: {last_message[:100]}... (waiting for image data)"
    
    def _refactor_server(self, messages):
        """Handle refactoring requests for code analysis"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a refactoring request
        if any(word in last_message.lower() for word in ["refactor", "refactoring", "quality", "lint", "analyze", "code review"]):
            # This is a simplified implementation. In a real implementation, the agent would need
            # to send code content to the refactoring server, but for now we'll just return a message
            # indicating what would happen.
            return f"Refactor server would analyze: {last_message[:100]}..."
        else:
            return f"Refactor server received: {last_message[:100]}... (waiting for code to analyze)"
    
    def _default_server_interaction(self, messages):
        """Default interaction for other server types"""
        last_message = messages[-1]["content"] if messages else ""
        return f"Server {self.server_name} received: {last_message[:100]}..."