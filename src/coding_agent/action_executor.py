"""
Action execution service for the CodingAgent.
Separates the action execution logic from the main agent class.
"""
from typing import Dict, Any, List, Tuple
from coding_agent.file_ops import FileOps
from coding_agent.git_ops import GitOps
from coding_agent.config import config_manager
from coding_agent.logger import agent_logger
import json


class ActionExecutor:
    """Handles execution of actions requested by the AI."""
    
    def __init__(self):
        self.file_ops = FileOps()
        self.git_ops = GitOps()
        self.config = config_manager.get_agent_config()
        
    def execute_actions(self, reply: str, search_provider=None) -> Tuple[str, bool]:
        """Parse JSON from LLM reply and execute actions."""
        try:
            # Extract JSON from LLM reply (even in markdown code blocks)
            start = reply.find("{")
            if start == -1:  # No JSON found
                return reply, False
            end = reply.rfind("}") + 1
            if end == 0:  # No closing brace found
                return reply, False

            json_str = reply[start:end]
            out = json.loads(json_str)
            actions = out.get("actions", [])
            results = [f"**Agent Plan:** {out.get('explanation', '')}\n"]

            for action in actions:
                if action["type"] == "read_file":
                    content = self.file_ops.read_file(action["path"])
                    results.append(f"🔹 Read `{action['path']}`:\n{content}")
                    agent_logger.log_file_operation("read", action["path"], True, "File read successfully")
                elif action["type"] == "write_file":
                    res = self.file_ops.write_file(action["path"], action["content"])
                    if res is True:
                        results.append(f"✅ Wrote `{action['path']}`.")
                        agent_logger.log_file_operation("write", action["path"], True, "File written successfully")
                    else:
                        results.append(f"❌ Error writing `{action['path']}`: {res}")
                        agent_logger.log_file_operation("write", action["path"], False, str(res))
                elif action["type"] == "append_to_file":
                    res = self.file_ops.append_to_file(action["path"], action["content"])
                    if res is True:
                        results.append(f"✅ Appended to `{action['path']}`.")
                        agent_logger.log_file_operation("append", action["path"], True, "Content appended successfully")
                    else:
                        results.append(f"❌ Error appending to `{action['path']}`: {res}")
                        agent_logger.log_file_operation("append", action["path"], False, str(res))
                elif action["type"] == "delete_file":
                    res = self.file_ops.delete_file(action["path"])
                    if res is True:
                        results.append(f"🗑️ Deleted `{action['path']}`.")
                        agent_logger.log_file_operation("delete", action["path"], True, "File deleted successfully")
                    else:
                        results.append(f"❌ Error deleting `{action['path']}`: {res}")
                        agent_logger.log_file_operation("delete", action["path"], False, str(res))
                elif action["type"] == "list_files":
                    pattern = action.get("pattern", "**/*.py")  # Default pattern if not specified
                    files = self.file_ops.list_files(pattern)
                    if isinstance(files, list) and not any(f.startswith("Error:") for f in files):
                        results.append(f"📋 Found {len(files)} files matching '{pattern}':\n" + "\n".join(f"- {f}" for f in files))
                        agent_logger.log_file_operation("list", pattern, True, f"Listed {len(files)} files")
                    else:
                        error_msg = files[0] if isinstance(files, list) else str(files)
                        results.append(f"❌ Error listing files with pattern '{pattern}': {error_msg}")
                        agent_logger.log_file_operation("list", pattern, False, error_msg)
                elif action["type"] == "create_directory":
                    res = self.file_ops.create_directory(action["path"])
                    if res is True:
                        results.append(f"📁 Created directory `{action['path']}`.")
                        agent_logger.log_file_operation("create_dir", action["path"], True, "Directory created successfully")
                    else:
                        results.append(f"❌ Error creating directory `{action['path']}`: {res}")
                        agent_logger.log_file_operation("create_dir", action["path"], False, str(res))
                elif action["type"] == "git_commit":
                    self.git_ops.stage_files(".")
                    cm = self.git_ops.commit(action["message"])
                    results.append(f"✅ Git commit: {action['message']}")
                    agent_logger.log_file_operation("git", "git commit", True, f"Committed with message: {action['message']}")
                elif action["type"] == "web_search":
                    # Handle web search if provider is available
                    if search_provider:
                        from coding_agent.provider.mcp import MCPProvider
                        if isinstance(search_provider, MCPProvider) and search_provider.server_name == 'duckduckgo':
                            # Create a message to send to the search provider
                            import time

                            search_messages = [
                                {"role": "user", "content": f"Search for information about: {action['query']}"}
                            ]
                            search_start = time.time()
                            answer = search_provider.chat(search_messages)
                            search_duration = time.time() - search_start
                            results.append(f"🌐 DuckDuckGo search for '{action['query']}':\n{answer}\n")
                            agent_logger.log_api_call("duckduckgo", "search", 200, search_duration)
                        else:
                            results.append(f"⚠️ Invalid search provider for query: {action['query']}")
                    else:
                        results.append(f"⚠️ No search provider available for query: {action['query']}")
                        agent_logger.app_logger.warning(f"No search provider available for query: {action['query']}")
                elif action["type"] == "analyze_code":
                    from coding_agent.code_analyzer import CodeAnalyzer
                    analyzer = CodeAnalyzer()
                    # Get the file content first if path is provided
                    if "path" in action:
                        # Read the file content
                        content = self.file_ops.read_file(action["path"])
                        if content.startswith("Error:"):
                            results.append(f"❌ Error reading file to analyze: {content}")
                        else:
                            analysis_result = analyzer.analyze_code(action["path"], content)
                            suggestions = analyzer.get_code_suggestions(analysis_result)
                            results.append(f"🔍 Code analysis for `{action['path']}`:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions))
                    # If content is directly provided instead of a path
                    elif "content" in action and "filename" in action:
                        analysis_result = analyzer.analyze_code(action["filename"], action["content"])
                        suggestions = analyzer.get_code_suggestions(analysis_result)
                        results.append(f"🔍 Code analysis for `{action['filename']}`:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions))
                    else:
                        results.append("❌ Error: analyze_code action requires either 'path' or both 'content' and 'filename' parameters")

            return "\n".join(results), True
        except json.JSONDecodeError as e:
            agent_logger.log_error("JSON_PARSE_ERROR", str(e), "Invalid JSON in LLM response")
            return reply, False
        except Exception as e:
            agent_logger.log_error("ACTION_EXECUTION_ERROR", str(e), "Error processing action")
            return f"Error processing action: {str(e)}", False