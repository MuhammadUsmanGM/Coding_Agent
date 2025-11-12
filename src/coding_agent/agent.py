# src/agent.py

import json
from typing import Dict, Any, List, Optional, Tuple
from coding_agent.provider.multiprovider import MultiProvider
from coding_agent.provider.groq import GroqProvider
from coding_agent.provider.google import GoogleProvider
from coding_agent.provider.mcp import MCPProvider
from coding_agent.file_ops import FileOps
from coding_agent.git_ops import GitOps
from coding_agent.mcp_manager import mcp_manager
from coding_agent.history_manager import HistoryManager
from dotenv import load_dotenv
load_dotenv()

class CodingAgent:
    def __init__(self) -> None:
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
        self.file_ops = FileOps()
        self.git_ops = GitOps()
        self.history: List[Dict[str, str]] = []
        self.history_manager = HistoryManager()
        
        # Check if we have a search MCP provider available
        self.search_provider = None
        for provider in self.providers:
            if hasattr(provider, 'server_name') and provider.server_name == 'duckduckgo':
                self.search_provider = provider

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

    def system_prompt(self) -> str:
        # Read additional agent instructions from AGENT.md
        agent_instructions = ""
        try:
            import os
            agent_md_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AGENT.md")
            if os.path.exists(agent_md_path):
                with open(agent_md_path, 'r', encoding='utf-8') as f:
                    agent_instructions = f.read()
        except Exception:
            # If reading the file fails, continue with just the base instructions
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

    def ask(self, prompt: str, max_tokens: int = 2048) -> str:
        # Compose dialogue for LLM
        messages = [{"role": "system", "content": self.system_prompt()}]
        messages += self.history + [{"role": "user", "content": prompt}]
        # Get LLM response
        reply = self.llm.chat(messages, max_tokens)
        # Try to parse/action JSON; else conversational reply
        result, performed = self._try_parse_and_execute(reply)
        response = result if performed else reply
        self.history.append({"role": "user", "content": prompt})
        self.history.append({"role": "assistant", "content": response})
        
        # Save the conversation to history
        self.history_manager.save_conversation(prompt, response)
        
        return response

    def _try_parse_and_execute(self, reply: str) -> Tuple[str, bool]:
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
                elif action["type"] == "write_file":
                    res = self.file_ops.write_file(action["path"], action["content"])
                    if res is True:
                        results.append(f"✅ Wrote `{action['path']}`.")
                    else:
                        results.append(f"❌ Error writing `{action['path']}`: {res}")
                elif action["type"] == "git_commit":
                    self.git_ops.stage_files(".")
                    cm = self.git_ops.commit(action["message"])
                    results.append(f"✅ Git commit: {action['message']}")
                elif action["type"] == "web_search":
                    # Use the MCP-based search instead of Tavily
                    if self.search_provider:
                        # Create a message to send to the search provider
                        search_messages = [
                            {"role": "user", "content": f"Search for information about: {action['query']}"}
                        ]
                        answer = self.search_provider.chat(search_messages)
                        results.append(f"🌐 DuckDuckGo search for '{action['query']}':\n{answer}\n")
                    else:
                        results.append(f"⚠️ No search provider available for query: {action['query']}")
            return "\n".join(results), True
        except json.JSONDecodeError:
            return reply, False
        except Exception as e:
            return f"Error processing action: {str(e)}", False

    def reset_history(self) -> None:
        self.history = []