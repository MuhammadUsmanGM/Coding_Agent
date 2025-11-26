"""
MCP (Model Context Protocol) Provider for the Coding Agent
"""
import requests
from typing import Optional, List, Dict, Any
from codeius.provider.base import ProviderBase
from codeius.core.mcp_manager import mcp_manager


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
            elif self.server_name == "diff":
                return self._diff_server(messages)
            elif self.server_name == "automation":
                return self._automation_server(messages)
            elif self.server_name == "visualization":
                return self._visualization_server(messages)
            elif self.server_name == "self_documenting":
                return self._self_documenting_server(messages)
            elif self.server_name == "package_inspector":
                return self._package_inspector_server(messages)
            elif self.server_name == "snippet_manager":
                return self._snippet_manager_server(messages)
            elif self.server_name == "web_scraper":
                return self._web_scraper_server(messages)
            elif self.server_name == "config_manager":
                return self._config_manager_server(messages)
            elif self.server_name == "task_scheduler":
                return self._task_scheduler_server(messages)
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
    
    def _diff_server(self, messages):
        """Handle diff requests for comparing files"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a diff request
        if any(word in last_message.lower() for word in ["diff", "compare", "difference", "vs"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # file paths to the diff server, but for now we'll just return a message
            # indicating what would happen.
            return f"Diff server would compare files from: {last_message[:100]}..."
        else:
            return f"Diff server received: {last_message[:100]}... (waiting for files to compare)"
    
    def _automation_server(self, messages):
        """Handle automation requests for scaffolding, env management, and renaming"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest an automation request
        if any(word in last_message.lower() for word in ["scaffold", "project", "create", "template"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # scaffolding requests to the automation server, but for now we'll just return a message
            # indicating what would happen.
            return f"Automation server would handle scaffolding for: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["env", "environment", "variable", ".env"]):
            return f"Automation server would manage environment variables for: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["rename", "variable", "change name"]):
            return f"Automation server would handle variable renaming for: {last_message[:100]}..."
        else:
            return f"Automation server received: {last_message[:100]}... (scaffold/env/rename)"
    
    def _visualization_server(self, messages):
        """Handle visualization requests for plotting metrics and data"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a visualization request
        if any(word in last_message.lower() for word in ["plot", "chart", "graph", "visualize", "visualization", "data"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # plotting requests to the visualization server, but for now we'll just return a message
            # indicating what would happen.
            return f"Visualization server would create plots for: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["metric", "coverage", "complexity", "test"]):
            return f"Visualization server would plot metrics for: {last_message[:100]}..."
        else:
            return f"Visualization server received: {last_message[:100]}... (waiting for data to plot)"
    
    def _self_documenting_server(self, messages):
        """Handle self-documenting requests for updating documentation"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a documentation update request
        if any(word in last_message.lower() for word in ["authors", "contributor", "author"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # author update requests to the self-documenting server, but for now we'll just return a message
            # indicating what would happen.
            return f"Self-documenting server would update authors based on: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["changelog", "change", "log"]):
            return f"Self-documenting server would update changelog based on: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["readme", "read me", "documentation"]):
            return f"Self-documenting server would update README based on: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["doc", "document", "update"]):
            return f"Self-documenting server would update documentation based on: {last_message[:100]}..."
        else:
            return f"Self-documenting server received: {last_message[:100]}... (authors/changelog/readme)"
    
    def _package_inspector_server(self, messages):
        """Handle package inspection requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a package inspection request
        if any(word in last_message.lower() for word in ["inspect", "package", "dependency", "requirement", "license", "vulnerability"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # package inspection requests to the package inspector server, but for now we'll just return a message
            # indicating what would happen.
            return f"Package inspector server would inspect: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["pip", "install", "requirements"]):
            return f"Package inspector server would analyze requirements from: {last_message[:100]}..."
        else:
            return f"Package inspector server received: {last_message[:100]}... (inspect/package)"
    
    def _snippet_manager_server(self, messages):
        """Handle snippet management requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a snippet management request
        if any(word in last_message.lower() for word in ["snippet", "template", "boilerplate", "code", "reuse"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # snippet requests to the snippet manager server, but for now we'll just return a message
            # indicating what would happen.
            return f"Snippet manager server would handle snippets for: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["code", "template", "pattern", "example"]):
            return f"Snippet manager server would provide code templates for: {last_message[:100]}..."
        else:
            return f"Snippet manager server received: {last_message[:100]}... (snippet/template)"
    
    def _web_scraper_server(self, messages):
        """Handle web scraping requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a web scraping request
        if any(word in last_message.lower() for word in ["scrape", "html", "parse", "beautifulsoup", "bs4", "web"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # scraping requests to the web scraper server, but for now we'll just return a message
            # indicating what would happen.
            return f"Web scraper server would scrape content for: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["extract", "data", "content", "document"]):
            return f"Web scraper server would extract content for: {last_message[:100]}..."
        else:
            return f"Web scraper server received: {last_message[:100]}... (scrape/html)"
    
    def _config_manager_server(self, messages):
        """Handle configuration management requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a configuration management request
        if any(word in last_message.lower() for word in ["config", "setting", "credential", "env", "environment", ".env", "yaml", "toml", "configuration"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # config management requests to the config manager server, but for now we'll just return a message
            # indicating what would happen.
            return f"Config manager server would handle configuration for: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["secret", "password", "token", "key", "auth", "authentication"]):
            return f"Config manager server would securely store credentials from: {last_message[:100]}..."
        else:
            return f"Config manager server received: {last_message[:100]}... (config/settings)"
    
    def _task_scheduler_server(self, messages):
        """Handle task scheduling requests"""
        last_message = messages[-1]["content"] if messages else ""
        
        # Look for keywords that suggest a task scheduling request
        if any(word in last_message.lower() for word in ["schedule", "cron", "task", "automate", "repeat", "timer", "interval"]):
            # This is a simplified implementation. In a real implementation, the agent would send
            # scheduling requests to the task scheduler server, but for now we'll just return a message
            # indicating what would happen.
            return f"Task scheduler server would schedule task for: {last_message[:100]}..."
        elif any(word in last_message.lower() for word in ["run", "execute", "test", "check", "command"]):
            return f"Task scheduler server would schedule execution of: {last_message[:100]}..."
        else:
            return f"Task scheduler server received: {last_message[:100]}... (schedule/task)"
    
    def _default_server_interaction(self, messages):
        """Default interaction for other server types"""
        last_message = messages[-1]["content"] if messages else ""
        return f"Server {self.server_name} received: {last_message[:100]}..."