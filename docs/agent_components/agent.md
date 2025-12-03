# Codeius AI Agent System

## Overview
The Codeius AI Agent is the central intelligence of the Codeius AI Coding Assistant. It orchestrates multiple services to provide a comprehensive coding assistance experience, integrating LLM providers, action executors, security scanners, and more.

## Core Components

### 1. CodingAgent Class
The main agent class that ties together all functionality:

```python
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
```

### 2. Model Management
The agent supports multiple LLM providers:

- **Google Provider**: Google's Gemini models
- **Groq Provider**: High-speed inference with Groq's API
- **Custom Provider**: Any OpenAI-compatible API
- **MCP Servers**: Internal services for specialized tasks

The model manager handles:
- Dynamic model switching
- Rate limiting and quotas
- Fallback mechanisms
- Performance monitoring

### 3. Conversation Management
- Maintains conversation history
- Context awareness
- Memory management to prevent overflow
- Session persistence
- Conversation summarization

### 4. Action Execution
The agent can execute various actions:
- File operations (read, write, delete, list)
- Git operations (clone, commit, push, pull)
- Shell command execution (safe commands only)
- Web searches
- Start and manage background processes
- Code execution in sandboxed environments
- Database queries
- Documentation searches
- OCR operations
- Refactoring operations
- Visualization creation

### 5. Security Features
- Input validation and sanitization
- Path traversal prevention
- File operation safety checks
- Security scanning of code
- Secrets detection in files
- Policy enforcement
- Plugin sandboxing
- API key security

## Agent Capabilities

### File Operations
```
{
  "type": "read_file",
  "path": "relative/to/workspace"
}
{
  "type": "write_file", 
  "path": "relative/to/workspace",
  "content": "file content"
}
{
  "type": "append_to_file",
  "path": "relative/to/workspace",
  "content": "additional content"
}
{
  "type": "delete_file",
  "path": "relative/to/workspace"
}
{
  "type": "list_files",
  "pattern": "**/*.py"
}
{
  "type": "create_directory",
  "path": "relative/to/workspace"
}
```

### Git Operations
```
{
  "type": "git_commit", 
  "message": "Commit message"
}
{
  "type": "git_push",
  "remote": "origin",
  "branch": "main"
}
{
  "type": "git_pull",
  "remote": "origin", 
  "branch": "main"
}
{
  "type": "git_clone",
  "url": "https://github.com/user/repo.git",
  "destination": "local/path"
}
```

### Process Management
```
{
  "type": "start_process",
  "command": "python script.py"
}
{
  "type": "send_input",
  "pid": 123,
  "data": "input data"
}
{
  "type": "read_output", 
  "pid": 123
}
{
  "type": "read_error",
  "pid": 123
}
{
  "type": "stop_process",
  "pid": 123
}
```

### Web Search
```
{
  "type": "web_search",
  "query": "search terms"
}
```

### Code Execution
```
{
  "type": "execute_python",
  "code": "print('Hello, World!')",
  "timeout": 30
}
```

## Response Format
When the agent needs to take actions, it responds in JSON format:

```
{
  "explanation": "Describe the plan and reasoning",
  "actions": [
    {"type": "read_file", "path": "..."},
    {"type": "write_file", "path": "...", "content": "..."},
    {"type": "web_search", "query": "..."},
    ...
  ]
}
```

If only a conversational response is needed, the agent replies in plain text.

## Security Implementation
The agent includes multiple security layers:
1. Path validation to prevent traversal attacks
2. Binary file detection to prevent reading binary content
3. File extension validation
4. Workspace boundary enforcement
5. API key validation and security
6. Command execution safety
7. Input sanitization
8. Plugin sandboxing

## Performance Optimization
- Caching for expensive operations
- Rate limiting to prevent API abuse
- Asynchronous operations where appropriate
- Memory management for conversation history
- Efficient file I/O operations
- Performance monitoring and logging

## Extensibility
The agent is designed to be extensible through:
- MCP (Model Context Protocol) servers for new capabilities
- Plugin system for custom functionality
- Custom model providers for different LLMs
- Event system for custom behaviors