# README.md

# Codeius AI Coding Agent

Codeius is an AI-powered coding assistant that helps with various programming tasks through a command-line interface. It can read and write files, perform git operations, and conduct web searches to assist with coding tasks.

## Features

- **File Operations**: Read and write source files in your workspace
- **Git Operations**: Stage and commit files
- **Web Search**: Perform real-time web searches using Tavily API
- **Multiple LLM Providers**: Uses both Groq and Google AI models with automatic failover
- **Model Switching**: Switch between available models using `/models` and `/switch` commands
- **Rich CLI Interface**: Beautiful, user-friendly command-line interface

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd coding-agent
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Configuration

Create a `.env` file in your project root with the following environment variables:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
GROQ_API_MODEL=llama3-70b-8192  # Optional, defaults to llama3-70b-8192
GOOGLE_API_MODEL=gemini-1.5-flash  # Optional, defaults to gemini-1.5-flash
```

## Usage

Run the agent using:

```bash
coding-agent
```

### Available Commands

- `/models` - List available AI models
- `/switch [model_key]` - Switch to a specific model
- `exit`, `quit`, or `bye` - Exit the application

### Example Usage

```
⌨️ Enter your query: Write a Python function to calculate factorial
🤖 Codeius Agent: [Response from the AI]
```

## Architecture

The agent follows a modular architecture:

- `agent.py` - Main agent logic and orchestration
- `cli.py` - Command-line interface
- `file_ops.py` - File system operations
- `git_ops.py` - Git operations
- `provider/` - LLM provider implementations
  - `groq.py` - Groq API integration
  - `google.py` - Google API integration
  - `multiprovider.py` - Logic for switching between providers
  - `tavily.py` - Web search functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

[Specify your license here]