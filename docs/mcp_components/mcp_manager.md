# MCP (Model Context Protocol) Components

## Overview
The Model Context Protocol (MCP) enables the Codeius AI Coding Agent to connect with various specialized tools and services. These MCP servers provide additional capabilities beyond core LLM functionality, such as code execution, file system access, web searching, and more.

## Architecture
MCP servers run as independent Flask services that expose standardized endpoints for interaction with the main agent. Each server implements specific functionality and communicates with the agent via HTTP requests/responses.

## Available MCP Servers

### 1. Code Runner Server
- **Purpose**: Execute Python code in a secure environment
- **Endpoint**: `/api/code_runner`
- **Capabilities**:
  - Execute Python snippets safely
  - Capture stdout/stderr
  - Set execution timeouts
  - Limit resource usage
- **Security**: Sandboxed execution environment with limited access

### 2. Filesystem Server
- **Purpose**: Safely read and write files within the workspace
- **Endpoint**: `/api/filesystem`
- **Capabilities**:
  - Read file contents
  - Write file contents
  - List directory contents
  - Create/delete directories
  - Check file existence
- **Security**: Path validation to prevent traversal, workspace boundary enforcement

### 3. Shell Server
- **Purpose**: Execute safe shell commands
- **Endpoint**: `/api/shell`
- **Capabilities**:
  - Execute basic shell commands
  - Capture command output
  - Set execution timeouts
- **Security**: Limited to safe commands, input sanitization, timeout protection

### 4. DuckDuckGo Search Server
- **Purpose**: Perform web searches without requiring API keys
- **Endpoint**: `/api/search`
- **Capabilities**:
  - Query web search engine
  - Return search results
  - Handle search result parsing
- **Security**: No API key required, anonymous requests

### 5. Code Search Server
- **Purpose**: Search for functions, classes, and TODOs in the codebase
- **Endpoint**: `/api/code_search`
- **Capabilities**:
  - Search for function definitions
  - Search for class definitions
  - Find TODO comments
  - Search in specific file types
  - Semantic search capabilities
- **Security**: Limits search to project workspace

### 6. Doc Search Server
- **Purpose**: Search documentation files in the workspace
- **Endpoint**: `/api/doc_search`
- **Capabilities**:
  - Search Markdown documentation
  - Search API documentation
  - Search README files
  - Perform full-text search on documentation
- **Security**: Restricts search to project documentation

### 7. Database Server
- **Purpose**: Query local SQLite databases
- **Endpoint**: `/api/database`
- **Capabilities**:
  - Execute SQL SELECT queries
  - Retrieve query results
  - Handle table introspection
- **Security**: Read-only mode for safety, path validation

### 8. OCR Server
- **Purpose**: Extract text from images
- **Endpoint**: `/api/ocr`
- **Capabilities**:
  - Extract text from image files
  - Handle multiple image formats (JPG, PNG, etc.)
  - Process image content to text
- **Security**: Limited to allowed image formats

### 9. Refactor Server
- **Purpose**: Analyze and refactor code
- **Endpoint**: `/api/refactor`
- **Capabilities**:
  - Analyze code structure
  - Identify code smells
  - Suggest improvements
  - Perform automated refactoring
- **Security**: No destructive operations, read-only analysis

### 10. Diff Server
- **Purpose**: Compare files and directories
- **Endpoint**: `/api/diff`
- **Capabilities**:
  - Compare file contents
  - Show differences
  - Compare directory structures
  - Generate diff reports
- **Security**: Limits access to workspace files only

### 11. Testing Server
- **Purpose**: Run automated tests
- **Endpoint**: `/api/testing`
- **Capabilities**:
  - Run Python unit tests
  - Execute test suites
  - Report test results
  - Handle test execution timeouts
- **Security**: Limited to test files in workspace

### 12. Visualization Server
- **Purpose**: Create plots and charts
- **Endpoint**: `/api/viz`
- **Capabilities**:
  - Generate matplotlib plots
  - Create data visualizations
  - Plot metrics and statistics
  - Save charts to files
- **Security**: Sandboxed execution environment

### 13. Automation Server
- **Purpose**: Handle project scaffolding and automation tasks
- **Endpoint**: `/api/automation`
- **Capabilities**:
  - Create project scaffolding
  - Generate boilerplate code
  - Environment setup
  - Variable renaming across files
- **Security**: Workspace-bound operations only

### 14. Self-Doc Server
- **Purpose**: Auto-update documentation files
- **Endpoint**: `/api/self_doc`
- **Capabilities**:
  - Update README files
  - Update changelogs
  - Update author information
  - Generate code documentation
- **Security**: Limits to documentation files

### 15. Package Inspector Server
- **Purpose**: Inspect packages and dependencies
- **Endpoint**: `/api/package_inspector`
- **Capabilities**:
  - Check package licenses
  - List dependencies
  - Identify vulnerabilities
  - Check package metadata
- **Security**: Restricted to installed packages

### 16. Snippet Manager Server
- **Purpose**: Manage code snippets and templates
- **Endpoint**: `/api/snippet_manager`
- **Capabilities**:
  - Store code snippets
  - Retrieve code snippets
  - Organize snippets by category
  - Insert snippets into code
- **Security**: Workspace-limited operations

### 17. Web Scraper Server
- **Purpose**: Extract content from web pages
- **Endpoint**: `/api/web_scraper`
- **Capabilities**:
  - Scrape web content
  - Extract specific elements
  - Download web resources
  - Parse HTML content
- **Security**: Limits to specified domains

### 18. Config Manager Server
- **Purpose**: Manage configuration files and credentials
- **Endpoint**: `/api/config_manager`
- **Capabilities**:
  - Read configuration files
  - Update configuration values
  - Manage environment files (.env)
  - Handle credential storage
- **Security**: Secure credential handling

### 19. Task Scheduler Server
- **Purpose**: Schedule tasks to run automatically
- **Endpoint**: `/api/task_scheduler`
- **Capabilities**:
  - Schedule commands to run later
  - Run periodic tasks
  - Handle task execution
  - Manage task queues
- **Security**: Validates scheduled commands, time limits

### 20. Git Server
- **Purpose**: Handle Git operations
- **Endpoint**: `/api/git`
- **Capabilities**:
  - Git status checking
  - Add files to staging
  - Commit changes
  - Push to remote
  - Pull from remote
  - Clone repositories
  - Branch operations
  - View commit history
- **Security**: Validates Git operations, prevents destructive commands

## MCP Server Management

### Discovery
- Servers are registered with the MCP manager at startup
- Configuration allows enabling/disabling specific servers
- Dynamic server addition/removeal without restarting the agent

### Communication Protocols
- Standardized HTTP/REST API for all servers
- JSON-based request/response format
- Consistent error handling across all servers
- Request validation and sanitization

### Security Considerations
- Each server implements its own security measures
- Input validation at the communication level
- Rate limiting for server requests
- Timeout protection for server operations
- Authentication for sensitive operations when appropriate

## Integration with Agent
MCP servers are tightly integrated with the agent through the MCPProvider class, which:
- Manages server connections
- Handles communication protocols
- Provides standardized interfaces to the agent
- Implements fallback mechanisms
- Manages server status and health checks

The MCP architecture allows for seamless expansion of agent capabilities while maintaining security and performance.