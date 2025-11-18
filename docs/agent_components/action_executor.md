# Action Executor Component Documentation

## Overview
The `action_executor.py` file contains the logic for safely executing actions requested by the AI agent. It acts as a security layer between the AI and the system, validating and executing various operations.

## Key Classes and Functions

### ActionExecutor Class
- **Purpose**: Executes actions requested by the AI while ensuring safety and security
- **Key Responsibilities**:
  - Validates requested actions against security policies
  - Executes file operations (read, write, delete, etc.)
  - Manages git operations
  - Handles external command execution

### Key Methods
- `execute_action(self, action_type, params)` - Main method to execute specific actions
- `execute_file_operations(self, operation, file_path, content=None)` - Handles file operations
- `execute_git_operations(self, operation, params)` - Handles git operations
- `validate_action(self, action_type, params)` - Validates actions before execution

## Security Measures
- Path validation to prevent traversal attacks
- File type checking to prevent execution of binary files
- Workspace restriction limiting operations to allowed paths
- Content validation for file write operations

## Dependencies
- `file_ops` - For secure file operations
- `git_ops` - For git operations
- `security_manager` - For security validation
- `error_handler` - For handling errors during execution

## Usage Context
This component is used by the main agent to safely execute actions requested by the AI model while ensuring system security.