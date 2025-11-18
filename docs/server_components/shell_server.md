# Shell Server Component Documentation

## Overview
The `shell_server.py` file implements a secure server for executing shell commands requested by the AI agent. It provides a safe way for the agent to execute system commands while maintaining security controls.

## Key Classes and Functions

### ShellServer Class
- **Purpose**: Provides a secure interface for executing shell commands
- **Key Responsibilities**:
  - Receives shell command requests via HTTP API
  - Validates commands for safety before execution
  - Executes approved commands in a controlled environment
  - Returns command output or errors
  - Implements command execution logging

### Security Features
- Command validation to prevent dangerous operations
- Output capture and sanitization
- Execution timeout to prevent hanging processes
- Logging of all executed commands
- Restricted command environment

## API Endpoints
- `POST /execute` - Execute a shell command with validation
- Request format: `{"command": "shell command"}`, `{"timeout": optional_timeout_seconds}`
- Response format: `{"success": boolean, "output": command_output, "error": potential_error}`

## Configuration
- Default port: 9400
- Configurable via environment variables
- Execution timeout limits
- Command validation rules

## Dependencies
- `flask` - For HTTP server functionality
- `subprocess` - For command execution
- `security_manager` - For command validation
- `logger` - For logging executed commands
- `config` - For server configuration

## Usage Context
This server is used by the agent when the `/shell` command is executed, providing a secure way for the AI to execute system commands while maintaining safety through validation and monitoring.