# Quick Start Guide

## Welcome to Codeius AI Coding Agent

This quick start guide will help you get up and running with the Codeius AI Coding Agent in just a few minutes. By the end of this guide, you'll be able to set up the agent, configure it, and start using its powerful features for coding assistance.

## Prerequisites

Before starting, ensure you have:
- Python 3.11 or higher installed
- `pip` package manager
- Git (optional, for cloning the repository)

## Step 1: Installation

Choose one of the following installation methods:

### Option 1: Install with pip (Recommended)
```bash
pip install codeius
```

### Option 2: Run without installation using uvx
```bash
uvx codeius
```

## Step 2: API Key Configuration

The agent requires API keys from AI providers. Get your keys from:

- **Groq API**: [https://console.groq.com/keys](https://console.groq.com/keys)
- **Google AI Studio**: [https://aistudio.google.com/](https://aistudio.google.com/)

Create a `.env` file in your project directory with:
```
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

## Step 3: Launch the Agent

You can use Codeius in two ways:

### Option 1: Command-Line Interface (CLI)
Start the agent with a rich CLI interface:
```bash
codeius
```

You should see a welcome interface with a prompt asking for your input.

### Option 2: Web-Based GUI
Start the agent with a modern web interface:
```bash
codeius web
```

This will start the backend server and display the URL where you can access the GUI in your browser.

## Step 4: Basic Interaction

Try your first interaction with the agent:

```
⌨️ Enter your query: Hello, can you explain what you do?
```

The agent will respond and explain its capabilities.

## Step 5: File Operations

Try asking the agent to help with a file in your project:

```
⌨️ Enter your query: Create a simple Python function that adds two numbers
```

The agent will generate the code for you.

## Step 6: Check Available Models

See what AI models are available:

```
/models
```

This command lists all available models you can switch between.

## Step 7: Switch Models

Switch to a different model if needed:

```
/switch google-gemini-pro
```

## Step 8: Explore Commands

Try these useful commands:

- `/help` - Show available commands
- `/context` - Show current project context
- `/search my_function` - Search for "my_function" in your codebase
- `/security_scan` - Run a security scan on your project

## Step 9: Advanced Features

### Adding Custom Models

Add your own AI model from any OpenAI-compatible API:

```
/add_model
```
Follow the prompts to enter your model details.

### Using Shell Commands

Execute shell commands securely:

```
/shell ls -la
```

### Mode Switching

Toggle between interaction and shell modes:

```
/toggle
```

## Step 10: Project-Specific Tasks

Try asking the agent to help with specific tasks relevant to your project. For example:

```
⌨️ Enter your query: Can you document the main function in src/main.py?
```

Or:

```
⌨️ Enter your query: Find all functions that handle user input validation
```

## Next Steps

Congratulations! You're now ready to use the Codeius AI Coding Agent. Here are suggestions for getting more out of the agent:

### Immediate Next Steps:

1. **Explore your codebase**: Use `/search` to find relevant code
2. **Set up project context**: Use `/set_project` if working with a specific project
3. **Try refactoring**: Ask the agent to improve existing code
4. **Run security checks**: Use `/security_scan` regularly

### Advanced Usage:

1. **Run additional servers** for enhanced functionality:
   - `python shell_server.py` (port 9400) - Enhanced shell commands
   - `python testing_server.py` (port 9500) - Automated testing
   - `python refactor_server.py` (port 9900) - Code refactoring tools

2. **Customize your experience** with different models and settings

3. **Explore the documentation** for more advanced features

## Troubleshooting Quick Fixes

- If you get an "API Key Not Found" error, verify your `.env` file has the correct API keys
- If commands aren't working, ensure they start with `/` (e.g., `/models`)
- If the agent is unresponsive, check your internet connection and API key validity

## Getting Help

- Use `/help` to see available commands
- Check the full documentation for detailed information
- If you encounter issues, refer to the troubleshooting guide

You're now ready to use the Codeius AI Coding Agent to enhance your development workflow! The agent will continue learning from your interactions to provide better assistance over time.