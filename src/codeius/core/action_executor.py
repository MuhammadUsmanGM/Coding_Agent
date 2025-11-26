"""
Action execution service for the CodingAgent.
Separates the action execution logic from the main agent class.
"""
from typing import Dict, Any, List, Tuple, Optional
from codeius.utils.file_ops import FileOps
from codeius.utils.git_ops import GitOps
from codeius.config import config_manager
from codeius.utils.logger import agent_logger
from codeius.core.action_handlers import ACTION_HANDLERS, ActionHandler
from codeius.core.performance import PerformanceMonitor
import json
import time


class ActionExecutor:
    """Handles execution of actions requested by the AI."""
    
    def __init__(self, perf_monitor: PerformanceMonitor):
        self.file_ops = FileOps()
        self.git_ops = GitOps()
        self.config = config_manager.get_agent_config()
        self.perf_monitor = perf_monitor
        
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
                action_type = action["type"]

                # Get the appropriate handler for this action type
                handler_class = ACTION_HANDLERS.get(action_type)
                if handler_class:
                    handler = handler_class(self.file_ops, self.git_ops)
                    
                    start_time = time.time()
                    success = False
                    try:
                        result, success = handler.handle(action, search_provider)
                    finally:
                        duration = time.time() - start_time
                        self.perf_monitor.record_operation(f"action_{action_type}", duration, success)

                    results.append(result)
                else:
                    result = f"❌ Unknown action type: {action_type}"
                    results.append(result)
                    agent_logger.log_error("UNKNOWN_ACTION_TYPE", action_type, f"Unknown action type: {action_type}")

            return "\n".join(results), True
        except json.JSONDecodeError as e:
            agent_logger.log_error("JSON_PARSE_ERROR", str(e), "Invalid JSON in LLM response")
            return reply, False
        except Exception as e:
            agent_logger.log_error("ACTION_EXECUTION_ERROR", str(e), "Error processing action")
            return f"Error processing action: {str(e)}", False