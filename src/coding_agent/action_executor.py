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
                            from coding_agent.logger import agent_logger
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
            return "\n".join(results), True
        except json.JSONDecodeError as e:
            agent_logger.log_error("JSON_PARSE_ERROR", str(e), "Invalid JSON in LLM response")
            return reply, False
        except Exception as e:
            agent_logger.log_error("ACTION_EXECUTION_ERROR", str(e), "Error processing action")
            return f"Error processing action: {str(e)}", False