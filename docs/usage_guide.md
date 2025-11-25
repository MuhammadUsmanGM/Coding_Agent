# Codeius AI Agent - Usage Guide

## Overview

This guide demonstrates how to use the various features of the Codeius AI Coding Agent with practical examples. The agent combines AI capabilities with specialized tools to assist in coding tasks.

## Core Features

### 1. Basic Interaction

The agent responds to natural language queries and can perform various coding-related tasks:

```
⌨️ Enter your query: Explain how to implement a binary search algorithm in Python
```

The agent will provide an explanation and code example.

### 2. File Operations

The agent can read, write, create, and modify files in your workspace:

```
⌨️ Enter your query: Read the file src/utils.py and analyze its functions
```

```
⌨️ Enter your query: Create a new file docs/api.md with documentation for our API endpoints
```

```
⌨️ Enter your query: Update the function in src/main.py to add input validation
```

### 3. Git Operations

The agent can perform git operations like committing changes:

```
⌨️ Enter your query: Create a git commit with message "Add user authentication feature"
```

### 4. Web Search

The agent can perform web searches to get current information:

```
⌨️ Enter your query: Search for best practices for handling database connections in Python
```

## Special Commands

### Model Management

Switch between different AI models:

```
/models                - List all available models
/switch groq-llama3-70b - Switch to a specific model
/add_model             - Add a custom AI model
```

### Agent Configuration

```
/context               - Show current project context
/set_project path name - Set project context
/search query          - Search codebase semantically
/find_function name    - Find a specific function
/find_class name       - Find a specific class
/file_context file     - Show context for a specific file
/autodetect            - Auto-detect project context
```

### Security Features

```
/security_scan         - Run comprehensive security scan
/secrets_scan          - Scan for secrets and sensitive information
/vuln_scan             - Scan for code vulnerabilities
/policy_check          - Check for policy violations
/security_policy       - Show current security policy settings
/security_report       - Generate comprehensive security report
/set_policy key value  - Update security policy settings
```

### Visual Interface

```
/themes                - Show available visual themes
/dashboard             - Show real-time code quality dashboard
/cls or /clear_screen  - Clear the screen and refresh the interface
```

### Mode Switching

```
/toggle or /mode       - Toggle between Interaction and Shell modes
/keys or /shortcuts    - Show mode switching options
```

## Detailed Usage Examples

### Example 1: Analyzing and Improving Code

```
⌨️ Enter your query: Read src/calculator.py and suggest improvements

🤖 Codeius Agent Response: [Analysis of the code with suggestions]

⌨️ Enter your query: Implement the suggested improvements to the calculator module

🤖 Codeius Agent Response: [Updated code with improvements applied]
```

### Example 2: Creating New Features

```
⌨️ Enter your query: Create a user authentication system with login and logout functions in the auth module

🤖 Codeius Agent Response: [Creates auth module with authentication functions]

⌨️ Enter your query: Create unit tests for the new authentication functions

🤖 Codeius Agent Response: [Creates test file with unit tests]
```

### Example 3: Code Refactoring

```
⌨️ Enter your query: Refactor the data processing functions in src/processor.py to improve readability

🤖 Codeius Agent Response: [Refactored code with improved structure]

⌨️ Enter your query: Run tests to ensure the refactored code still works correctly

🤖 Codeius Agent Response: [Test execution results]
```

### Example 4: Project Scaffolding

```
⌨️ Enter your query: Create a new Python project structure with src, tests, and docs directories

🤖 Codeius Agent Response: [Creates directory structure and basic files]

⌨️ Enter your query: Add a requirements.txt file with common dependencies

🤖 Codeius Agent Response: [Creates requirements.txt with dependencies]
```

### Example 5: Searching and Navigation

```
⌨️ Enter your query: Find all functions that handle user input validation

🤖 Codeius Agent Response: [List of functions found]

⌨️ Enter your query: Show me the context around the validate_email function

🤖 Codeius Agent Response: [Context information for the function]
```

## Advanced Features

### Custom Model Integration

Add your own AI models:

```
/add_model
```
Follow the prompts to enter model name, API key, base URL, and model ID.

Then switch to it:
```
/switch your-model-name
```

### Server-Based Tools

When MCP servers are running, the agent can access additional capabilities:

#### Code Analysis and Refactoring
- Semantic code search across project files
- Code quality analysis and refactoring suggestions
- Complexity measurement and optimization

#### Database Operations
- Safe queries on local SQLite databases
- Data inspection and reporting
- Schema analysis

#### Visualization
- Generate charts from code metrics
- Create plots for test coverage data
- Visualize database query results

#### Documentation Management
- Update AUTHORS, CHANGELOG, and README files automatically
- Manage configuration files in various formats (env, YAML, TOML, JSON)
- Extract documentation from source code

## Working with Different Model Providers

### Using Groq Models
- By default, the agent uses Groq's llama3-70b-8192 model
- Known for fast response times

### Using Google Models
- By default, uses Google's gemini-1.5-flash model
- Good for complex reasoning tasks

### Using Custom Models
- Add models from OpenAI, Anthropic, or custom endpoints
- Use `/add_model` command to configure

## Security Best Practices

1. Always review code changes before committing
2. Use the security scan features regularly
3. Check for secrets before committing code
4. Validate external dependencies
5. Review model responses for accuracy

## Troubleshooting Common Issues

### "API Key Not Found" Error
- Ensure you've set your environment variables correctly
- Verify your .env file contains the required API keys
- Restart the agent after setting new API keys

### File Operation Blocked
- The agent validates file paths to prevent unsafe operations
- Ensure you're working within the allowed workspace directory
- Check that file paths don't contain dangerous patterns

### Model Switching Issues
- Use `/models` to see available models
- Verify the model key matches exactly what's listed
- Check your API keys are valid for the selected provider

## Performance Tips

- Use semantic search to find relevant code quickly
- Keep conversation history manageable by clearing when needed
- Use appropriate models for different tasks (faster models for simple tasks)
- Leverage server tools for complex operations that don't require AI

## Integration with Development Workflow

The agent can be integrated into your development workflow:

1. **Code Generation**: Generate boilerplate code, tests, or documentation
2. **Code Review**: Analyze code for best practices and potential issues
3. **Refactoring**: Improve existing code structure and readability
4. **Testing**: Generate and run tests for your code
5. **Documentation**: Keep documentation up-to-date with code changes

This guide covers the essential features of the Codeius AI Coding Agent. Explore each feature to maximize your productivity and code quality.