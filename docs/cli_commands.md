# CLI Commands Reference

## Overview

The Codeius AI Coding Agent provides a rich set of commands to manage various aspects of the agent's functionality. This document details all available commands, their syntax, and usage examples.

## Command Structure

All agent commands start with a forward slash (`/`). The agent distinguishes between:

- **Direct AI queries**: Text that doesn't begin with `/`, which is sent to the AI
- **Agent commands**: Text beginning with `/` that performs specific agent functions

## Basic Commands

### /help
Shows help information about available commands.

**Usage:**
```
/help
```

**Output:** 
Displays a list of available commands with brief descriptions.

### /exit, /quit, /q
Exits the agent application.

**Usage:**
```
/exit
```

## Model Management Commands

### /models
Lists all available AI models and MCP tools.

**Usage:**
```
/models
```

**Output:**
A list showing:
- Available LLM providers
- Custom models if any are configured
- MCP servers that are connected

### /switch [model_key]
Switches to a specific AI model by its key.

**Usage:**
```
/switch groq-llama3-70b
```

**Parameters:**
- `model_key`: The key identifying the model you want to switch to (use `/models` to see available keys)

### /add_model
Adds a custom AI model from an OpenAI-compatible API endpoint.

**Usage:**
```
/add_model
```

**Process:**
- Follow the interactive prompts to enter:
  - Model name (for identification)
  - API key
  - Base URL (e.g., `https://api.openai.com/v1`)
  - Model ID (e.g., `gpt-4`)

## MCP Server Commands

### /mcp
Lists available MCP servers and their status.

**Usage:**
```
/mcp
```

**Output:**
A list of MCP servers that the agent can communicate with, including their endpoints and capabilities.

## File and Project Management Commands

### /context
Shows current project context information including workspace path, active settings, and project details.

**Usage:**
```
/context
```

### /set_project [path] [name]
Sets the current project context to the specified path with a given name.

**Usage:**
```
/set_project /path/to/project my-project
```

**Parameters:**
- `path`: The filesystem path to the project directory
- `name`: A friendly name for the project

### /file_context [file_path]
Shows context information for a specific file including its location, size, and basic information.

**Usage:**
```
/file_context src/main.py
```

**Parameters:**
- `file_path`: Path to the file to get context for

### /autodetect
Auto-detects and sets project context based on current directory structure.

**Usage:**
```
/autodetect
```

## Code Search and Navigation Commands

### /search [query]
Performs semantic search across the codebase for the specified query.

**Usage:**
```
/search user authentication
```

**Parameters:**
- `query`: The search query to look for in the codebase

### /find_function [name]
Finds a specific function by name in the codebase.

**Usage:**
```
/find_function validate_input
```

**Parameters:**
- `name`: The name of the function to find

### /find_class [name]
Finds a specific class by name in the codebase.

**Usage:**
```
/find_class UserHandler
```

**Parameters:**
- `name`: The name of the class to find

## Security Commands

### /security_scan
Runs a comprehensive security scan on the project.

**Usage:**
```
/security_scan
```

### /secrets_scan
Scans for secrets and sensitive information in the codebase.

**Usage:**
```
/secrets_scan
```

### /vuln_scan
Scans for code vulnerabilities.

**Usage:**
```
/vuln_scan
```

### /policy_check
Checks for policy violations in the project.

**Usage:**
```
/policy_check
```

### /security_policy
Shows current security policy settings.

**Usage:**
```
/security_policy
```

### /security_report
Generates a comprehensive security report.

**Usage:**
```
/security_report
```

### /set_policy [key] [value]
Updates security policy settings.

**Usage:**
```
/set_policy max_file_size 20
```

**Parameters:**
- `key`: The name of the policy setting to update
- `value`: The new value for the setting

## Interface and Display Commands

### /themes
Shows available visual themes.

**Usage:**
```
/themes
```

### /dashboard
Shows real-time code quality dashboard.

**Usage:**
```
/dashboard
```

### /cls, /clear_screen
Clears the screen and refreshes the interface.

**Usage:**
```
/cls
```

## Mode Management Commands

### /toggle, /mode
Toggles between Interaction and Shell modes.

**Usage:**
```
/toggle
```

**Modes:**
- **Interaction Mode**: Traditional blue-themed prompt (`⌨️ Enter your query:`)
- **Shell Mode**: Orange-themed prompt with shell icon (`🐚 Shell Mode:`), for direct command execution

## Development and Analysis Commands

### /shell [command]
Executes a direct shell command securely.

**Usage:**
```
/shell ls -la
```

**Parameters:**
- `command`: The shell command to execute

**Note:** Includes security checks to prevent dangerous operations.

### /analyze [file_path]
Analyzes a code file for quality, security, and style issues.

**Usage:**
```
/analyze src/main.py
```

**Parameters:**
- `file_path`: Path to the file to analyze

### /clear
Clears the conversation history.

**Usage:**
```
/clear
```

## Additional Commands

### /keys, /shortcuts
Shows mode switching options and keyboard shortcuts.

**Usage:**
```
/keys
```

### /history
Shows the conversation history (if implemented).

**Usage:**
```
/history
```

## Command Usage Examples

### Switching Models
```
/models
/switch google-gemini-pro
```

### Searching Code
```
/search error handling
/find_function process_request
```

### Working with Files
```
/file_context src/config.py
/context
```

### Security Operations
```
/security_scan
/secrets_scan
/set_policy max_file_size 15
```

### System Commands
```
/shell python -m pytest tests/
/toggle
/cls
```

## Command Limitations and Notes

1. **Command Parameters**: Most commands that take parameters require them in the same line after the command
2. **Path Parameters**: File paths should be relative to the project workspace or absolute paths
3. **Security**: Some commands may have restricted functionality based on security policies
4. **Dependencies**: MCP server-dependent commands require the appropriate servers to be running

## Error Handling

Commands may return various error messages:

- `Command not recognized`: Misspelled command or missing `/` prefix
- `Parameter missing`: Required parameters were not provided
- `Permission denied`: Security policy prevents the operation
- `Resource not found`: Requested file, model, or server not available

## Command Tips

1. **Tab Completion**: The CLI supports tab completion for commands
2. **History**: Use up/down arrows to navigate command history
3. **Help Context**: If unsure about a command, try using `/help` followed by the command name if supported
4. **Chain Commands**: You can execute commands in sequence to perform complex operations
5. **Mode Awareness**: Be aware of which mode you're in (Interaction vs Shell) as some commands behave differently