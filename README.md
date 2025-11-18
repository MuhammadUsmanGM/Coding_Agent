# Codeius AI Coding Agent

## ⚠️ IMPORTANT: API Key Setup Required

Before using Codeius, you need to obtain API keys from:
- [Groq](https://console.groq.com/keys) - Create an account and generate an API key
- [Google AI Studio](https://aistudio.google.com/) - Create an account and generate an API key

After getting your keys, set them as environment variables:

**On Linux/MacOS:**
```bash
export GROQ_API_KEY=your_groq_api_key
export GOOGLE_API_KEY=your_google_api_key
```

**On Windows:**
```cmd
set GROQ_API_KEY=your_groq_api_key
set GOOGLE_API_KEY=your_google_api_key
```

Or create a `.env` file in your project with:
```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
```

By default, Codeius uses:
- Groq model: `llama3-70b-8192` (can be changed via `GROQ_API_MODEL`)
- Google model: `gemini-1.5-flash` (can be changed via `GOOGLE_API_MODEL`)
- Base URLs are pre-configured in the application

---

Codeius is an advanced AI-powered coding assistant that helps with various programming tasks through a command-line interface. It can read and write files, perform git operations, run tests, search code, execute shell commands, and conduct web searches to assist with coding tasks. With enhanced security, performance, and a beautiful visual interface, Codeius is your intelligent coding companion.

## Features

- **File Operations**: Read and write source files in your workspace with advanced security validation
- **Git Operations**: Stage and commit files
- **Web Search**: Perform real-time web searches via DuckDuckGo MCP server (no API key required)
- **Multiple LLM Providers**: Uses both Groq and Google AI models with automatic failover
- **Model Switching**: Switch between available models using `/models` and `/switch` commands
- **Custom Model Support**: Add your own AI models with `/add_model` command and custom API endpoints
- **Rich CLI Interface**: Beautiful, user-friendly command-line interface with stunning visuals
- **Code Search & Navigation**: Find functions, classes, and TODOs in your project
- **Secure Shell Commands**: Execute safe shell commands directly with `/shell` command
- **Context Management**: Advanced project context tracking with semantic code search and cross-reference features
- **Advanced Security**: Built-in vulnerability scanning, secrets detection, and policy enforcement
- **Keyboard Shortcuts**: Enhanced navigation with special key combinations
- **Automated Testing**: Run pytest tests directly from the agent
- **Documentation Search**: Find information in local documentation files
- **Database Access**: Query local SQLite databases safely
- **Real-time Dashboard**: Monitor code quality, test coverage, and build status
- **Visual Recognition/OCR**: Extract text from images using OCR
- **Code Analysis & Quality**: Analyze code for style, security, and complexity issues
- **Code Refactoring & Quality**: Analyze code style, detect anti-patterns, and suggest refactorings
- **File/Directory Diff Tool**: Compare content of two files or directories for versioning and code reviews
- **Local Plugin System**: Extensible architecture allowing users to add custom tools by dropping in Python scripts
- **Script/Form Automation Tool**: Automate repetitive coding chores like scaffolding, environment management, and variable renaming
- **Data Visualization Tool**: Plot code metrics, test coverage, and database query results using matplotlib
- **Self-Documenting Agent**: Auto-update Markdown docs (AUTHORS, CHANGELOG, README) as code changes
- **Package Inspector**: Probe installed Python packages, license info, vulnerabilities, and dependencies offline
- **Snippet/Template Manager**: Store, retrieve, and insert boilerplate snippets for accelerating repetitive coding
- **Offline Web Scraping Tool**: Scrape static HTML files or local sites with BeautifulSoup, for documentation or data extraction tasks
- **Advanced Configuration/Settings Tool**: Interactive config/credentials manager for .env, YAML, or TOML settings—all changes local and secure
- **Scheduling/Task Automation Tool**: Local cron/task scheduler using schedule, letting the agent run commands, tests, or code checks automatically
- **Enhanced Security**: Multiple security layers to prevent path traversal, unauthorized access, and code injection
- **Performance Optimizations**: Caching, rate limiting, and efficient resource usage
- **Comprehensive Logging**: Detailed logs for debugging and monitoring
- **Type Safety**: Full type hinting throughout the codebase for better reliability

## Installation

### Option 1: Using pip (Recommended)

Install directly using pip:

```bash
pip install codeius
```

Then run:

```bash
codeius
```

### Option 2: Using uvx (Zero-Install)

Run Codeius directly without installation using uvx:

```bash
uvx codeius
```

### Option 3: Development Installation

If you want to contribute or modify the code:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd coding-agent
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   # Additional dependencies for enhanced functionality:
   pip install flask pytest pillow pytesseract radon flake8 matplotlib packaging beautifulsoup4 pyyaml toml schedule
   ```

3. To use the enhanced functionality including task scheduling:
   You will need to run the following server scripts in separate terminals (only those you plan to use):
   - `python code_search_server.py` (port 9300)
   - `python shell_server.py` (port 9400)
   - `python testing_server.py` (port 9500)
   - `python doc_search_server.py` (port 9600)
   - `python db_server.py` (port 9700)
   - `python ocr_server.py` (port 9800)
   - `python refactor_server.py` (port 9900)
   - `python diff_server.py` (port 10000)
   - `python automation_server.py` (port 10100)
   - `python viz_server.py` (port 10200)
   - `python self_doc_server.py` (port 10300)
   - `python package_inspector_server.py` (port 10400)
   - `python snippet_manager_server.py` (port 10500)
   - `python web_scraper_server.py` (port 10600)
   - `python config_manager_server.py` (port 10700)
   - `python task_scheduler_server.py` (port 10800)

## Configuration

Create a `.env` file in your project root with the following environment variables:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
GROQ_API_MODEL=llama3-70b-8192  # Optional, defaults to llama3-70b-8192
GOOGLE_API_MODEL=gemini-1.5-flash  # Optional, defaults to gemini-1.5-flash
MAX_TOKENS=2048  # Optional, default max tokens for LLM responses
CONVERSATION_HISTORY_LIMIT=50  # Optional, default number of conversation turns to keep
MAX_FILE_SIZE_MB=10  # Optional, maximum file size in MB that can be read
MAX_CONCURRENT_OPERATIONS=5  # Optional, maximum concurrent operations
RATE_LIMIT_REQUESTS=100  # Optional, rate limit for API calls per window
RATE_LIMIT_WINDOW_SECONDS=60  # Optional, time window for rate limiting
MCP_SERVER_TIMEOUT=30  # Optional, timeout for MCP server requests
MCP_SERVER_RETRY_ATTEMPTS=3  # Optional, number of retry attempts for MCP servers
WORKSPACE_ROOT=.  # Optional, root directory for file operations
```

## Usage

Run the agent using:

```bash
codeius
```

### Available Commands

- `/models` - List available AI models
- `/mcp` - List available MCP servers
- `/add_model` - Add a custom AI model with API key and endpoint
- `/shell [command]` - Execute a direct shell command securely
- `/toggle` - Toggle between Interaction and Shell modes
- `/mode` - Alternative command to toggle between modes
- `/context` - Show current project context information
- `/set_project [path] [name]` - Set the current project context
- `/search [query]` - Semantic search across the codebase
- `/find_function [name]` - Find a function by name
- `/find_class [name]` - Find a class by name
- `/file_context [file_path]` - Show context for a specific file
- `/autodetect` - Auto-detect and set project context
- `/security_scan` - Run comprehensive security scan
- `/secrets_scan` - Scan for secrets and sensitive information
- `/vuln_scan` - Scan for code vulnerabilities
- `/policy_check` - Check for policy violations
- `/security_policy` - Show current security policy settings
- `/security_report` - Generate comprehensive security report
- `/set_policy [key] [value]` - Update security policy settings
- `/keys` or `/shortcuts` - Show mode switching options
- `/themes` - Show available visual themes
- `/cls` or `/clear_screen` - Clear the screen and refresh the interface
- `/dashboard` - Show real-time code quality dashboard
- `/switch [model_key]` - Switch to a specific model
- `/exit` - Exit the application
- `/help` - Show help information
- `/clear` - Clear the conversation history
- `/analyze [file_path]` - Analyze code file for quality, security, and style issues
- And many more specialized tools for coding tasks

### Example Usage

```
⌨️ Enter your query: Write a Python function to calculate factorial
🤖 Codeius Agent: [Response from the AI]
```

### New Features

#### Custom Model Support (`/add_model`)
The agent now supports adding custom AI models from any OpenAI-compatible API endpoint:
1. Run `/add_model` command
2. Enter the model name for identification
3. Provide your API key (securely stored)
4. Enter the base URL (e.g., `https://api.openai.com/v1`)
5. Enter the model ID (e.g., `gpt-4`, `claude-3-opus`, or custom model identifier)
6. The model will be available in `/models` and can be switched to with `/switch`

This allows you to connect to various providers like OpenAI, Anthropic, Azure OpenAI, or custom APIs.

#### Secure Shell Command Execution (`/shell`)
Execute shell commands directly from the agent with security features:
- Run `/shell [command]` to execute any shell command securely
- Built-in security checks prevent dangerous operations (e.g., rm -rf, format, etc.)
- Command output is properly captured and displayed

#### Enhanced Mode Switching
- **Command Method**: Use `/toggle` or `/mode` command to switch between modes
- **Keyboard Shortcut**: Shift+! (Shift+Exclamation) is conceptually intended for mode switching (use `/toggle` command as primary method)

#### Visual Appearance Changes
- **Interaction Mode**: Traditional blue-themed prompt (`⌨️ Enter your query:`)
- **Shell Mode**: Orange-themed prompt with shell icon (`🐚 Shell Mode:`)
- **Visual Feedback**: Clear visual indicators when switching between modes

### Security Features
The agent includes multiple security layers:
- Path traversal prevention
- File type validation
- Binary file detection
- Workspace restriction
- API key validation
- Command execution safety (shell command blocking)
- Input sanitization

## Using with uvx

For the easiest access without installation, use `uvx`:

```bash
# Run directly from PyPI without installing
uvx codeius

# Install and run with uvx
uvx --with codeius codeius
```

uvx is a command-line tool that lets you run Python applications without installing them. It automatically creates a temporary environment, installs the app with its dependencies, runs it, and cleans up when you're done.

To install uvx:

```bash
pip install uv
```

## Architecture

The agent follows a modular, service-oriented architecture:

- `agent.py` - Main agent class that orchestrates other services
- `model_manager.py` - Handles model switching and LLM interactions
- `custom_model_manager.py` - Manages user-defined custom models
- `conversation_manager.py` - Manages conversation history and context
- `action_executor.py` - Executes actions requested by the AI
- `cli.py` - Command-line interface with enhanced visuals
- `file_ops.py` - Secure file system operations with validation
- `git_ops.py` - Git operations
- `dashboard.py` - Code quality dashboard
- `history_manager.py` - Conversation history management
- `mcp_manager.py` - MCP server management
- `config.py` - Configuration management system
- `logger.py` - Comprehensive logging system
- `error_handler.py` - Standardized error handling
- `performance.py` - Caching and performance optimizations
- `code_analyzer.py` - Code quality analysis and suggestions
- `provider/` - LLM provider implementations
  - `groq.py` - Groq API integration
  - `google.py` - Google API integration
  - `mcp.py` - MCP server integration
  - `custom.py` - Custom model provider integration
  - `multiprovider.py` - Logic for switching between providers
- Server scripts:
  - `code_search_server.py` - Code search functionality
  - `shell_server.py` - Safe shell command execution
  - `testing_server.py` - Automated testing
  - `doc_search_server.py` - Documentation search
  - `db_server.py` - Database queries

## Security Features

Codeius implements multiple security layers:
- Path traversal prevention
- File type validation
- Binary file detection
- Workspace restriction
- API key validation
- Rate limiting
- Plugin sandboxing
- Input sanitization

## Performance Optimizations

- API response caching
- Rate limiting
- Asynchronous operations
- Memory management
- Conversation history limiting
- Efficient file operations

## Troubleshooting on Windows

If you encounter issues on Windows related to terminal compatibility, try running Codeius from Command Prompt (cmd.exe) instead of PowerShell or other terminal emulators.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

## License

MIT License - see the LICENSE file for details.
</content>