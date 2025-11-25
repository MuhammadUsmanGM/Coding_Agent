# Codeius AI Coding Agent - Setup Guide

## Prerequisites

Before installing Codeius, ensure you have:

- Python 3.11 or higher
- `pip` package manager
- Git (optional, for cloning the repository)

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

## API Key Configuration

Codeius requires API keys from multiple providers to function. Follow these steps to configure them:

### 1. Obtain API Keys

You need to get API keys from:
- [Groq](https://console.groq.com/keys) - Create an account and generate an API key
- [Google AI Studio](https://aistudio.google.com/) - Create an account and generate an API key

### 2. Set Environment Variables

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

### 3. Create .env File (Recommended)

Alternatively, create a `.env` file in your project root with:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
```

The application will automatically load these variables from the `.env` file.

### 4. Using Custom Models

You can also add custom models from OpenAI-compatible API endpoints using the `/add_model` command within the agent interface.

## Configuration Options

You can customize various aspects of Codeius by setting environment variables:

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

## Running MCP Servers (Optional)

For enhanced functionality, you can run various MCP (Model Context Protocol) servers:

1. Navigate to your project directory
2. Run the server scripts corresponding to the features you want to use:

```bash
python code_search_server.py    # Port 9300 - Semantic code search
python shell_server.py          # Port 9400 - Secure shell commands
python testing_server.py        # Port 9500 - Automated testing
python doc_search_server.py     # Port 9600 - Documentation search
python db_server.py             # Port 9700 - Database operations
python ocr_server.py            # Port 9800 - OCR and image processing
python refactor_server.py       # Port 9900 - Code refactoring
python diff_server.py           # Port 10000 - File/directory diff tool
python automation_server.py     # Port 10100 - Script automation
python viz_server.py            # Port 10200 - Data visualization
python self_doc_server.py       # Port 10300 - Self-documentation
python package_inspector_server.py # Port 10400 - Package inspection
python snippet_manager_server.py   # Port 10500 - Code snippets
python web_scraper_server.py       # Port 10600 - Web scraping
python config_manager_server.py    # Port 10700 - Config management
python task_scheduler_server.py    # Port 10800 - Task scheduling
```

## Running Codeius

Once configured, run Codeius with:

```bash
codeius
```

This will start the interactive CLI interface where you can begin using the AI coding assistant.

## First Steps

After launching Codeius:

1. Use `/help` to see available commands
2. Use `/models` to list available AI models
3. Use `/mcp` to list available MCP servers
4. Start by asking a simple question or coding task to begin

## Verification

To verify your installation:

1. Make sure the CLI interface starts without errors
2. Test the `/models` command to see available AI models
3. Try a simple query to ensure the agent responds correctly