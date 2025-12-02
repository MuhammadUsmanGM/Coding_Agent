"""
Main agent class for the Codeius AI Coding Agent.
Orchestrates all services to provide an intelligent coding assistant.
"""
from typing import Dict, Any, List, Optional, Tuple
from codeius.core.model_manager import ModelManager
from codeius.core.conversation_manager import ConversationManager
from codeius.core.action_executor import ActionExecutor
from codeius.core.plugin_manager import plugin_manager
from codeius.config import config_manager
from codeius.utils.logger import agent_logger
from codeius.provider.mcp import MCPProvider
from codeius.core.custom_model_manager import custom_model_manager
from codeius.core.context_manager import ContextManager
from codeius.core.security_manager import SecurityScanner, security_scanner, security_policy_manager
from codeius.core.visualization_manager import VisualizationManager
from codeius.core.performance import perf_monitor
from dotenv import load_dotenv
import time
import os
import pathlib
from cachetools import cached, TTLCache

load_dotenv()

# Create a cache object with a TTL of 5 minutes
cache = TTLCache(maxsize=100, ttl=300)

class CodingAgent:
    """
    Main agent class that orchestrates all services to provide an intelligent coding assistant.

    The CodingAgent integrates multiple services to provide a comprehensive coding assistance
    experience, including model management, conversation handling, action execution,
    security scanning, and more.

    Attributes:
        config: Agent configuration settings
        model_manager: Handles LLM model selection and management
        conversation_manager: Manages conversation history and context
        action_executor: Executes actions requested by the AI
        plugin_manager: Manages user plugins
        context_manager: Manages project context
        security_scanner: Performs security scans
        security_policy_manager: Manages security policies
        visualization_manager: Handles visualization features
        providers: Available LLM providers
        search_provider: Available search provider (if any)
    """
    def __init__(self) -> None:
        # Load configuration
        self.config = config_manager.get_agent_config()

        # Initialize core services
        self.model_manager = ModelManager()
        self.conversation_manager = ConversationManager()
        self.action_executor = ActionExecutor(perf_monitor)
        self.plugin_manager = plugin_manager
        self.context_manager = ContextManager()
        self.security_scanner = security_scanner
        self.security_policy_manager = security_policy_manager
        self.visualization_manager = VisualizationManager(".")

        # Load user plugins
        self.plugin_manager.load_plugins()

        # Check if we have a search MCP provider available
        self.search_provider = None
        for provider in self.model_manager.providers:
            if hasattr(provider, 'server_name') and provider.server_name == 'duckduckgo':
                self.search_provider = provider

        # Add providers attribute for compatibility with existing code
        self.providers = self.model_manager.providers

        # Log initialization to file only, not to console
        # agent_logger.app_logger.info("CodingAgent initialized successfully")

    def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently active provider/model.

        Returns:
            Dictionary containing model information, or None if no model is active.
        """
        return self.model_manager.get_current_model_info()

    def get_available_models(self) -> Dict[str, Any]:
        """
        Get list of available AI models only (excluding MCP tools).

        Returns:
            Dictionary containing available models and their information.
        """
        return self.model_manager.get_available_models()

    def get_available_mcp_tools(self) -> Dict[str, Any]:
        """
        Get list of available MCP tools/servers.

        Returns:
            Dictionary containing available MCP tools and their information.
        """
        return self.model_manager.get_available_mcp_tools()

    def switch_model(self, model_key: str) -> str:
        """
        Switch to a specific model by key.

        Args:
            model_key: The key identifying the model to switch to.

        Returns:
            String indicating the result of the model switch operation.
        """
        result = self.model_manager.switch_model(model_key)
        if "Switched to" in result:
            agent_logger.app_logger.info(f"Model switched to {model_key}")
        else:
            agent_logger.app_logger.warning(f"Model switch failed: {model_key} not found")
        return result

    def system_prompt(self) -> str:
        """
        Generate system prompt with agent instructions.

        Reads additional agent instructions from AGENT.md and combines them
        with core tool capabilities to form the complete system prompt.

        Returns:
            Formatted system prompt string for the LLM.
        """
        # Read additional agent instructions from AGENT.md
        agent_instructions = ""
        try:
            # Correctly resolve the path to AGENT.md in the project root
            current_file_path = pathlib.Path(__file__).resolve()
            project_root = current_file_path.parent.parent.parent  # Go up to project root directory
            agent_md_path = project_root / "AGENT.md"
            if agent_md_path.exists():
                with open(agent_md_path, 'r', encoding='utf-8') as f:
                    agent_instructions = f.read()
            else:
                # Fallback if AGENT.md is not found
                agent_instructions = "You are an advanced AI coding agent."
        except Exception as e:
            # If reading the file fails, continue with just the base instructions
            agent_logger.app_logger.warning(f"Failed to read AGENT.md: {e}")
            agent_instructions = ""

        return (
            f"{agent_instructions}\n\n"
            "Core Tools Available:\n"
            "- Read and write source files in the workspace\n"
            "- Perform git operations (stage, commit)\n"
            "- Perform web searches using DuckDuckGo via MCP server\n"
            "- Start and interact with background processes\n"
            "When you need to take action, reply with JSON using this structure:\n"
            "{\n"
            " \"explanation\": \"Describe your plan\",\n"
            " \"actions\": [\n"
            "   {\"type\": \"read_file\",         \"path\": \"...\"},\n"
            "   {\"type\": \"write_file\",        \"path\": \"...\", \"content\": \"...\"},\n"
            "   {\"type\": \"append_to_file\",    \"path\": \"...\", \"content\": \"...\"},\n"
            "   {\"type\": \"delete_file\",       \"path\": \"...\"},\n"
            "   {\"type\": \"list_files\",        \"pattern\": \"...\"},\n"
            "   {\"type\": \"create_directory\",  \"path\": \"...\"},\n"
            "   {\"type\": \"git_commit\",        \"message\": \"...\"},\n"
            "   {\"type\": \"web_search\",        \"query\": \"...\"},\n"
            "   {\"type\": \"analyze_code\",      \"path\": \"...\"},\n"
            "   {\"type\": \"start_process\",     \"command\": \"...\"},\n"
            "   {\"type\": \"send_input\",        \"pid\": 123, \"data\": \"...\"},\n"
            "   {\"type\": \"read_output\",       \"pid\": 123},\n"
            "   {\"type\": \"read_error\",        \"pid\": 123},\n"
            "   {\"type\": \"stop_process\",      \"pid\": 123}\n"
            " ]\n"
            "}\n\n"
            "If only a conversation or non-code answer is needed, reply conversationally."
        )

    def ask(self, prompt: str, max_tokens: Optional[int] = None):
        """
        Process a user prompt and return the agent's response.

        Args:
            prompt: The user's input prompt
            max_tokens: Optional maximum number of tokens for the response
                        (defaults to config value if not provided)

        Returns:
            The agent's response to the user's prompt
        """
        # Use configured max tokens if not explicitly provided
        if max_tokens is None:
            max_tokens = self.config.max_tokens

        # Compose dialogue for LLM
        messages = [{"role": "system", "content": self.system_prompt()}]
        messages += self.conversation_manager.get_conversation_context() + [{"role": "user", "content": prompt}]

        # Get LLM response with timing
        start_time = time.time()
        try:
            reply = self.model_manager.chat(messages, max_tokens)
            success = True
        except Exception as e:
            reply = f"Error communicating with LLM: {e}"
            success = False
        duration = time.time() - start_time
        perf_monitor.record_operation("llm_chat", duration, success)

        # Add to conversation history
        self.conversation_manager.add_message("user", prompt)

        # Try to parse/action JSON; else conversational reply
        result, executed = self.action_executor.execute_actions(reply, self.search_provider)
        if executed:
            self.conversation_manager.add_message("assistant", result)
            return result
        else:
            self.conversation_manager.add_message("assistant", reply)
            return reply

    def reset_history(self) -> None:
        """Reset the conversation history."""
        self.conversation_manager.reset_history()

    def list_custom_models(self) -> Dict[str, Any]:
        """
        Get list of custom models.

        Returns:
            Dictionary containing all custom model information.
        """
        return self.model_manager.list_custom_models()

    def add_custom_model(self, name: str, api_key: str, base_url: str, model: str) -> bool:
        """
        Add a custom model to the agent.

        Args:
            name: Name for the custom model
            api_key: API key for the model
            base_url: Base URL for the API
            model: Model identifier

        Returns:
            True if the model was added successfully, False otherwise
        """
        return self.model_manager.add_custom_model(name, api_key, base_url, model)