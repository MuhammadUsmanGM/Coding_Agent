# Codeius AI Agent Documentation

Welcome to the comprehensive documentation for the Codeius AI Coding Agent. This documentation is organized by component to help you understand and work with the various parts of the system.

## Directory Structure

```
doc/
├── agent_components/          # Core agent functionality
│   ├── agent.md              # Main agent class
│   ├── action_executor.md    # Action execution logic
│   └── conversation_manager.md # Conversation management
├── cli_components/            # Command-line interface
│   └── cli.md                # CLI implementation
├── llm_providers/             # LLM provider implementations
│   ├── groq.md               # Groq API integration
│   └── google.md             # Google Generative AI integration
├── security_components/       # Security-related components
│   └── security_manager.md   # Security management
├── model_components/          # Model management
│   └── model_manager.md      # Model switching and management
├── utilities/                 # Utility components
│   ├── file_ops.md           # Secure file operations
│   ├── logger.md             # Logging system
│   ├── error_handler.md      # Error handling system
│   ├── context_manager.md    # Project context management
│   ├── dashboard.md          # Dashboard implementation
│   ├── git_ops.md            # Git operations
│   └── config.md             # Configuration management
├── server_components/         # External server components
│   ├── automation_server.md  # Automation tasks (scaffolding, renaming, env management)
│   ├── code_search_server.md # Code search functionality
│   ├── config_manager_server.md # Config/credentials management
│   ├── db_server.md          # Database operations (SQLite)
│   ├── diff_server.md        # File/directory comparison
│   ├── doc_search_server.md  # Documentation search
│   ├── ocr_server.md         # OCR and image text extraction
│   ├── package_inspector_server.md # Package inspection
│   ├── refactor_server.md    # Code refactoring tools
│   ├── self_doc_server.md    # Self-documentation updates
│   ├── shell_server.md       # Shell command server
│   ├── snippet_manager_server.md # Code snippets management
│   ├── task_scheduler_server.md # Task automation and scheduling
│   ├── viz_server.md         # Data visualization
│   └── web_scraper_server.md # Web scraping functionality
├── mcp_components/            # Model Context Protocol
│   └── mcp_manager.md        # MCP management
├── templates/                 # Project templates
│   └── react_template.md     # React project template
├── plugin_components/         # Plugin system
│   └── plugin_manager.md     # Plugin management
├── visualization_components/  # Data visualization
│   └── visualization_manager.md # Visualization tools
├── refactor_components/       # Code refactoring tools
│   └── refactor_server.md    # Refactoring server
├── search_components/         # Search functionality
│   └── code_search_server.md # Code search server
├── setup_guide.md             # Installation and setup guide
├── custom_model_guide.md      # Custom model integration guide
└── README.md                 # This file
```

## Component Categories

### Agent Components
Core functionality for the AI agent including conversation management, action execution, and the main agent class.

### CLI Components
Command-line interface elements that provide the user interaction layer.

### LLM Providers
Different AI model providers like Groq, Google, and custom endpoints.

### Security Components
Security measures including validation, sanitization, and access controls.

### Model Components
Components for managing different AI models and switching between them.

### Utilities
General-purpose utilities for logging, configuration, file operations, etc.

### Server Components
External server implementations for various tools and services.

### MCP Components
Model Context Protocol implementations for tool integration.

### Templates
Project scaffolding templates for different tech stacks.

### Plugin Components
Extensibility system for adding custom functionality.

### Visualization Components
Data visualization and charting capabilities.

### Refactor Components
Code analysis and refactoring tools.

### Search Components
Code search and indexing functionality.

## Getting Started

To understand the system, start with the main components:

1. [Setup Guide](setup_guide.md) - Complete installation and configuration instructions
2. [Agent Component](agent_components/agent.md) - The core of the system
3. [CLI Component](cli_components/cli.md) - The user interface
4. [Model Manager](model_components/model_manager.md) - How models are managed
5. [Custom Model Guide](custom_model_guide.md) - Adding custom AI models
6. [Security Manager](security_components/security_manager.md) - Security measures

## Contributing

When contributing to the documentation, please follow the existing structure and ensure each component documentation includes:

- Overview of the component's purpose
- Key classes and functions
- Dependencies and usage context
- Any important features or capabilities