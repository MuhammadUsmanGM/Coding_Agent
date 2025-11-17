# src/agent.py

from typing import Dict, Any, List, Optional, Tuple
from coding_agent.model_manager import ModelManager
from coding_agent.conversation_manager import ConversationManager
from coding_agent.action_executor import ActionExecutor
from coding_agent.plugin_manager import plugin_manager
from coding_agent.config import config_manager
from coding_agent.logger import agent_logger
from coding_agent.provider.mcp import MCPProvider
from dotenv import load_dotenv
import time
import os
load_dotenv()

class CodingAgent:
    def __init__(self) -> None:
        # Load configuration
        self.config = config_manager.get_agent_config()

        # Initialize core services
        self.model_manager = ModelManager()
        self.conversation_manager = ConversationManager()
        self.action_executor = ActionExecutor()
        self.plugin_manager = plugin_manager

        # Load user plugins
        self.plugin_manager.load_plugins()

        # Check if we have a search MCP provider available
        self.search_provider = None
        for provider in self.model_manager.providers:
            if hasattr(provider, 'server_name') and provider.server_name == 'duckduckgo':
                self.search_provider = provider

        # Add providers attribute for compatibility with existing code
        self.providers = self.model_manager.providers

        # Log initialization
        agent_logger.app_logger.info("CodingAgent initialized successfully")

    def get_current_model_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the currently active provider/model"""
        return self.model_manager.get_current_model_info()

    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available AI models only (excluding MCP tools)"""
        return self.model_manager.get_available_models()

    def get_available_mcp_tools(self) -> Dict[str, Any]:
        """Get list of available MCP tools/servers"""
        return self.model_manager.get_available_mcp_tools()

    def switch_model(self, model_key: str) -> str:
        """Switch to a specific model by key"""
        result = self.model_manager.switch_model(model_key)
        if "Switched to" in result:
            agent_logger.app_logger.info(f"Model switched to {model_key}")
        else:
            agent_logger.app_logger.warning(f"Model switch failed: {model_key} not found")
        return result

    def system_prompt(self) -> str:
        """Generate system prompt with agent instructions."""
        # Read additional agent instructions from AGENT.md
        agent_instructions = ""
        try:
            agent_md_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AGENT.md")
            if os.path.exists(agent_md_path):
                with open(agent_md_path, 'r', encoding='utf-8') as f:
                    agent_instructions = f.read()
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
            "When you need to take action, reply with JSON using this structure:\n"
            "{\n"
            " \"explanation\": \"Describe your plan\",\n"
            " \"actions\": [\n"
            "   {\"type\": \"read_file\",  \"path\": \"...\"},\n"
            "   {\"type\": \"write_file\", \"path\": \"...\", \"content\": \"...\"},\n"
            "   {\"type\": \"git_commit\", \"message\": \"...\"},\n"
            "   {\"type\": \"web_search\", \"query\": \"...\"}\n"
            " ]\n"
            "}\n"
            "If only a conversation or non-code answer is needed, reply conversationally."
        )

    def ask(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Process user input and return agent response."""
        # Use configured max tokens if not explicitly provided
        if max_tokens is None:
            max_tokens = self.config.max_tokens

        # Compose dialogue for LLM
        messages = [{"role": "system", "content": self.system_prompt()}]
        messages += self.conversation_manager.get_conversation_context() + [{"role": "user", "content": prompt}]

        # Get LLM response with timing
        start_time = time.time()
        reply = self.model_manager.chat(messages, max_tokens)
        duration = time.time() - start_time

        # Try to parse/action JSON; else conversational reply
        result, performed = self.action_executor.execute_actions(reply, self.search_provider)
        response = result if performed else reply

        # Add messages to conversation
        self.conversation_manager.add_message("user", prompt)
        self.conversation_manager.add_message("assistant", response)

        # Save the conversation to history
        self.conversation_manager.save_conversation(prompt, response)

        # Log the activity
        agent_logger.log_agent_activity(prompt, response, [])

        # Log API call timing
        agent_logger.log_api_call("llm", "chat", 200, duration)

        return response

    def reset_history(self) -> None:
        """Reset conversation history."""
        self.conversation_manager.reset_history()