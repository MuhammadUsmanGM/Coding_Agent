# Git MCP Server

## Overview
The Git MCP (Model Context Protocol) server provides version control capabilities to the Codeius AI Coding Agent. It allows the AI to perform Git operations through standardized API endpoints.

## Purpose
This server enables the AI agent to perform Git operations such as:
- Checking repository status
- Adding files to staging
- Committing changes
- Pushing and pulling from remote repositories
- Cloning repositories
- Managing branches
- Viewing commit history
- Managing remotes

## Endpoints

### GET /status
- **Purpose**: Get the git status of the current repository
- **Parameters**: 
  - `repo_path` (optional, defaults to current directory)
- **Response**: 
  - Success: `{ "output": "git status output", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### POST /add
- **Purpose**: Add files to git staging area
- **Request Body**:
  - `files`: String or Array of file paths to add (default: '.')
  - `repo_path`: Path to repository (optional, defaults to current directory)
- **Response**: 
  - Success: `{ "output": "operation info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### POST /commit
- **Purpose**: Commit staged changes
- **Request Body**:
  - `message`: Commit message (default: "Auto-commit from Codeius")
  - `repo_path`: Path to repository (optional, defaults to current directory)
- **Response**:
  - Success: `{ "output": "commit info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### POST /push
- **Purpose**: Push changes to remote repository
- **Request Body**:
  - `remote`: Remote name (default: 'origin')
  - `branch`: Branch name (default: 'main')
  - `repo_path`: Path to repository (optional, defaults to current directory)
- **Response**:
  - Success: `{ "output": "push info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### POST /pull
- **Purpose**: Pull changes from remote repository
- **Request Body**:
  - `remote`: Remote name (default: 'origin')
  - `branch`: Branch name (default: 'main')
  - `repo_path`: Path to repository (optional, defaults to current directory)
- **Response**:
  - Success: `{ "output": "pull info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### POST /clone
- **Purpose**: Clone a remote repository
- **Request Body**:
  - `url`: Repository URL to clone
  - `destination`: Destination path (optional, defaults to current directory)
- **Response**:
  - Success: `{ "output": "clone info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### POST /branch
- **Purpose**: Create or switch branches
- **Request Body**:
  - `create`: Branch name to create (optional)
  - `switch`: Branch name to switch to (optional)
  - `repo_path`: Path to repository (optional, defaults to current directory)
- **Response**:
  - Success: `{ "output": "branch info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### GET /log
- **Purpose**: Show git log
- **Query Parameters**:
  - `repo_path`: Path to repository (optional, defaults to current directory)
  - `limit`: Number of commits to return (default: 10)
- **Response**:
  - Success: `{ "output": "log info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### GET /diff
- **Purpose**: Show git diff
- **Query Parameters**:
  - `repo_path`: Path to repository (optional, defaults to current directory)
  - `staged`: Whether to show staged changes only (default: false)
- **Response**:
  - Success: `{ "output": "diff info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### POST /remote
- **Purpose**: Manage git remotes
- **Request Body**:
  - `add`: Name of remote to add (optional)
  - `set_url`: Name of remote to update URL (optional)
  - `url`: URL for the remote
  - `repo_path`: Path to repository (optional, defaults to current directory)
- **Response**:
  - Success: `{ "output": "remote info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

### POST /init
- **Purpose**: Initialize a new git repository
- **Request Body**:
  - `repo_path`: Path where to initialize repository (optional, defaults to current directory)
  - `bare`: Boolean to create a bare repository (optional, default: false)
- **Response**:
  - Success: `{ "output": "init info", "success": true }`
  - Error: `{ "error": "error message", "success": false }`

## Security Features
- Path validation to prevent directory traversal
- Timeout mechanism for Git operations (60 seconds)
- Input validation for all parameters
- Sanitization of Git operation parameters
- Workspace boundary checks

## Integration with Agent
- Registered as an MCP server in the MCP manager
- Available through the MCP provider system
- Can be accessed by the AI agent with proper authorization
- Follows MCP protocol standards

## Performance Considerations
- Operations are executed with timeouts to prevent hanging
- Background execution for long-running operations
- Resource usage monitoring
- Caching of frequently requested information

## Error Handling
- Comprehensive error messages with context
- Timeout handling with appropriate messages
- Validation errors for invalid parameters
- Git command execution errors with output capture