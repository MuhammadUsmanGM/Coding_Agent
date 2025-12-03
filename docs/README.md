# Codeius AI Coding Agent - Architecture Overview

## Introduction
Codeius is an advanced AI-powered coding assistant that helps developers with various programming tasks. It integrates with multiple LLM providers, offers a rich command-line interface, and provides a web-based GUI for enhanced user experience.

## Project Structure

```
src/
├── codeius/                # Main package
│   ├── api/                # API server for backend services
│   ├── cli/                # Command-line interface components
│   ├── core/               # Core agent functionality
│   ├── provider/           # LLM provider implementations
│   ├── servers/            # MCP (Model Context Protocol) servers
│   ├── templates/          # Project scaffolding templates
│   ├── utils/              # Utility functions and helpers
│   ├── __init__.py
│   ├── cli.py              # Main CLI entry point
│   ├── config.py           # Configuration management
│   └── main.py             # Application entry point
Codeius-GUI/               # React frontend application
├── public/
├── src/
│   ├── components/         # UI components
│   ├── services/           # API service functions
│   ├── utils/              # Utility functions
│   ├── App.jsx            # Main application component
│   ├── index.jsx          # Application entry point
│   └── App.css            # Main stylesheet
docs/                     # Documentation
├── agent_components/      # Agent-specific documentation
├── cli_components/        # CLI-specific documentation
├── llm_providers/         # LLM provider documentation
├── mcp_components/        # MCP server documentation
├── model_components/      # Model management documentation
├── plugin_components/     # Plugin system documentation
├── refactor_components/   # Refactoring tools documentation
├── search_components/     # Search functionality documentation
├── security_components/   # Security documentation
├── server_components/     # Backend server documentation
├── templates/             # Template documentation
├── utilities/             # Utility documentation
├── visualization_components/ # Visualization documentation
├── git_controls/          # Git operations and GUI controls
├── gui_components/        # GUI-specific components
├── AGENT.md              # AI agent instructions
├── LICENSE.md            # License information
├── README.md             # Main documentation file
├── quick_start_guide.md  # Quick start instructions
├── setup_guide.md        # Setup guide
├── usage_guide.md        # Usage guide
├── security_guide.md     # Security guide
├── troubleshooting_guide.md # Troubleshooting guide
├── custom_model_guide.md # Custom model guide
└── cli_commands.md       # CLI command reference
```

## Core Architecture

### 1. Agent System
- **CodingAgent**: Main orchestrator that manages all services
- **ModelManager**: Handles switching between different LLM providers
- **ConversationManager**: Manages conversation history and context
- **ActionExecutor**: Executes actions requested by the AI
- **ContextManager**: Manages project context and file analysis
- **SecurityManager**: Performs security scans and policy enforcement
- **Performance Monitor**: Tracks operation performance and metrics

### 2. LLM Providers
- **Google Provider**: Integration with Google's Gemini API
- **Groq Provider**: Integration with Groq's API for fast inference
- **Custom Provider**: Support for any OpenAI-compatible API
- **MCP Providers**: Integration with internal MCP servers

### 3. MCP (Model Context Protocol) Servers
- **Code Runner**: Execute Python code in secure environment
- **Filesystem**: Safe file read/write operations with validation
- **DuckDuckGo Search**: Web search capabilities
- **Code Search**: Search for functions, classes, and TODOs in codebase
- **Shell**: Execute safe shell commands
- **Testing**: Run automated tests
- **Documentation Search**: Search local and online documentation
- **Database**: Query local SQLite databases
- **OCR**: Extract text from images
- **Refactor**: Analyze and refactor code
- **Diff**: Compare files and directories
- **Automation**: Scaffolding, environment management, renaming
- **Visualization**: Create plots and charts
- **Self-Doc**: Auto-update documentation files
- **Package Inspector**: Inspect packages and dependencies
- **Snippet Manager**: Manage code snippets and templates
- **Web Scraper**: Extract content from websites/files
- **Config Manager**: Manage configuration files and credentials
- **Task Scheduler**: Schedule tasks to run automatically
- **Git Server**: Comprehensive version control operations (git status, add, commit, push, pull, clone, branch management, etc.)

### 4. User Interfaces

#### Command-Line Interface (CLI)
- Beautiful terminal UI with theming support
- Multi-line input with syntax highlighting
- Command history and context awareness
- Keyboard shortcuts and special key combinations
- Model switching capabilities
- File operation commands
- Git integration
- Security scanning tools

#### Web-Based GUI (React)
- Modern React interface with rich components
- Real-time chat interface for conversations
- File upload and management
- Code editor with syntax highlighting
- Dashboard for analytics and metrics
- Settings panel for configuration
- Command palette for quick actions
- Project explorer for file management
- Git controls for version control operations

### 5. Security Features
- Path traversal prevention
- File type validation
- Binary file detection
- Workspace restriction
- API key validation
- Rate limiting
- Plugin sandboxing
- Input sanitization
- Security policy management
- Secrets detection
- Vulnerability scanning

### 6. Plugin System
- Extensible architecture for custom functionality
- Plugin discovery and loading mechanism
- Plugin lifecycle management
- Secure execution environment
- Plugin metadata and configuration

### 7. Performance Features
- API response caching
- Rate limiting
- Asynchronous operations
- Memory management
- Conversation history limiting
- Efficient file operations
- Performance monitoring

### 8. Configuration Management
- Environment variable support
- YAML configuration files
- Model-specific settings
- Theme customization
- Key binding customization
- Project-specific preferences

## Integration Points

### Backend API
- Flask-based REST API
- WebSocket support for real-time features
- CORS enabled for cross-origin requests
- Session management
- Authentication mechanisms
- File upload handling

### Frontend Integration
- React-based single-page application
- REST API communication
- WebSocket connections
- State management with React hooks
- Component-based architecture
- Responsive design

## Development Workflow
1. User sends request to CLI or web interface
2. Request processed by the CodingAgent
3. Agent selects appropriate model/provider
4. Response analyzed for required actions
5. Actions executed using available tools
6. Results returned to user interface
7. Conversation history updated

## Deployment Options
- Standalone CLI application
- Web-based GUI application
- Docker container deployment
- Cloud deployment with scaling
- Local installation via pip

## Technologies Used
- Python 3.11+
- React 18+
- Flask for backend APIs
- Rich for CLI interfaces
- WebSockets for real-time features
- MongoDB for data storage
- Docker for containerization