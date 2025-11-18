# Agent Component Documentation

## Overview
The `agent.py` file contains the core `CodingAgent` class, which orchestrates the entire AI coding assistant functionality. It manages interactions with LLMs, handles conversation context, and coordinates with various tools and services.

## Key Classes and Functions

### CodingAgent Class
- **Purpose**: Main class that manages the AI coding assistant functionality
- **Key Responsibilities**:
  - Interacts with multiple LLM providers (Groq, Google, etc.)
  - Manages conversation history and context
  - Coordinates with tools (file operations, git ops, security scans, etc.)
  - Handles execution of requested actions

### Key Methods
- `__init__(self, ...)` - Initializes the agent with models, tools, and configuration
- `ask(self, prompt, max_tokens=None)` - Main method to process user input and return agent response
- `system_prompt(self)` - Generates the system prompt with agent instructions
- `execute_action(self, action, params)` - Executes actions requested by the AI

## Dependencies
- `model_manager` - For managing LLM models
- `action_executor` - For executing requested actions
- `conversation_manager` - For managing conversation history
- `context_manager` - For handling project context
- `mcp_manager` - For managing MCP servers
- `logger` - For logging agent activities

## Usage Context
This component is the central hub of the application, used by the CLI to process user requests and coordinate with other components and services.