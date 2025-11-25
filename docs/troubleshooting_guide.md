# Troubleshooting Guide

## Overview

This troubleshooting guide provides solutions to common issues you may encounter when using the Codeius AI Coding Agent. Each section addresses specific problems with potential causes and solutions.

## Common Issues and Solutions

### 1. API Key Configuration Issues

#### Problem: "API Key Not Found" Error
**Symptoms**: Agent fails to start or gives errors about missing API keys.

**Causes and Solutions**:
- **Environment variables not set**: Ensure GROQ_API_KEY and GOOGLE_API_KEY are set in your environment.
  ```bash
  # On Linux/MacOS:
  export GROQ_API_KEY=your_groq_api_key
  export GOOGLE_API_KEY=your_google_api_key
  
  # On Windows:
  set GROQ_API_KEY=your_groq_api_key
  set GOOGLE_API_KEY=your_google_api_key
  ```
  
- **.env file not in correct location**: Ensure your `.env` file is in the project root directory.
  ```
  GROQ_API_KEY=your_groq_api_key
  GOOGLE_API_KEY=your_google_api_key
  ```

- **Invalid API key format**: Verify that your API keys are properly formatted and not expired.

#### Problem: "Invalid API Key" Error
**Causes and Solutions**:
- **Expired key**: Generate a new API key from the provider's dashboard.
- **Insufficient permissions**: Ensure your API key has the necessary permissions for the required operations.
- **Wrong key for provider**: Make sure you're using the correct API key for the correct provider.

### 2. File Operation Issues

#### Problem: "File Operation Blocked" or "Path Validation Error"
**Symptoms**: Cannot read, write, or modify files.

**Causes and Solutions**:
- **Access outside workspace**: The agent restricts operations to the project workspace. Ensure the file path is within your project directory.
- **Path traversal attempt**: Check for patterns like `../` or `..\\` in file paths.
- **File format restriction**: The agent may block certain file types for security reasons.

#### Problem: "File Not Found" Error
**Causes and Solutions**:
- **Incorrect file path**: Verify the file path is correct and relative to the workspace root.
- **File doesn't exist**: Check if the file has been deleted or moved.
- **Case sensitivity**: On some systems, file names are case-sensitive.

#### Problem: "Permission Denied" Error
**Causes and Solutions**:
- **Insufficient file permissions**: Check file permissions and ensure the agent has read/write access.
- **File in use**: Close any other applications using the file.
- **Read-only file system**: Check if the file system is mounted as read-only.

### 3. Model and AI Issues

#### Problem: "Model Not Responding" or "Request Timeout"
**Symptoms**: Agent stops responding or takes too long to generate responses.

**Causes and Solutions**:
- **Network connectivity issues**: Check your internet connection.
- **API rate limits**: You may have exceeded the API provider's rate limits. Wait and retry.
- **High API usage**: Try switching to a different model that may have higher availability.
- **Provider downtime**: Check the status of the API provider.

#### Problem: "Model Switch Failed"
**Symptoms**: The `/switch` command doesn't change the active model.

**Causes and Solutions**:
- **Invalid model key**: Use `/models` to see the correct model keys and use the exact name.
- **Model not loaded**: Restart the agent to reload all models.
- **Connection issues**: Check API key validity and network connectivity.

### 4. Server-Related Issues

#### Problem: MCP Server Not Responding
**Symptoms**: Commands that depend on MCP servers fail with connection errors.

**Causes and Solutions**:
- **Server not running**: Start the required MCP server (e.g., `python shell_server.py` for port 9400).
- **Wrong port**: Verify the server is running on the expected port (check settings.json).
- **Network issues**: Check firewall settings that may block local connections.
- **Server error**: Check the server console for error messages.

#### Problem: "Port Already in Use" Error
**Symptoms**: Server fails to start due to port conflicts.

**Causes and Solutions**:
- **Another instance running**: Stop any other instances using the same port.
- **Process holding port**: Find and terminate processes using the port:
  ```bash
  # On Linux/MacOS:
  lsof -i :9400  # To find the process using port 9400
  kill -9 <PID>  # To kill the process (replace <PID> with actual process ID)
  
  # On Windows:
  netstat -ano | findstr :9400
  taskkill /PID <PID> /F
  ```

### 5. Installation Issues

#### Problem: "Module Not Found" Error
**Symptoms**: Agent fails to start with missing module errors.

**Causes and Solutions**:
- **Incomplete installation**: Reinstall the package with all dependencies:
  ```bash
  pip install -e .
  pip install flask pytest pillow pytesseract radon flake8 matplotlib packaging beautifulsoup4 pyyaml toml schedule
  ```
- **Virtual environment not activated**: Activate your virtual environment before running the agent.
- **Dependency conflicts**: Create a fresh virtual environment and install dependencies.

#### Problem: "Import Error" After Installation
**Symptoms**: Agent starts but encounters import errors during operation.

**Causes and Solutions**:
- **Python version incompatibility**: Ensure you're using Python 3.11 or higher.
- **Missing optional dependencies**: Install the required optional dependencies based on your needs.

### 6. Command Interface Issues

#### Problem: Commands Not Recognized
**Symptoms**: Agent doesn't respond to commands like `/models`, `/mcp`, etc.

**Causes and Solutions**:
- **Wrong input format**: Ensure you're using the correct command format (e.g., `/models` not `models`).
- **Command mode confusion**: In shell mode, some commands may behave differently. Use `/toggle` to switch modes.
- **Typo in command**: Check for typos in the command name.

#### Problem: CLI Interface Display Issues
**Symptoms**: Visual elements don't display correctly or interface looks broken.

**Causes and Solutions**:
- **Terminal compatibility**: Try running in Command Prompt on Windows instead of PowerShell or other terminals.
- **Rich library issues**: Update the rich library: `pip install --upgrade rich`
- **Prompt toolkit issues**: Update prompt-toolkit: `pip install --upgrade prompt-toolkit`

### 7. Performance Issues

#### Problem: Slow Response Times
**Symptoms**: Agent takes too long to respond to queries or commands.

**Causes and Solutions**:
- **Network latency**: Check your internet connection quality to API providers.
- **Large file operations**: The agent may slow down with very large files. Consider processing files in smaller chunks.
- **Multiple MCP servers**: Running many servers can consume resources. Only run necessary servers.
- **Model processing time**: Some models are inherently slower. Try switching to a faster model.

#### Problem: High Memory Usage
**Symptoms**: Agent consumes excessive memory or system becomes sluggish.

**Causes and Solutions**:
- **Large conversation history**: Use `/clear` to clear conversation history periodically.
- **Large file processing**: Avoid loading very large files into conversations.
- **Multiple processes**: Check for multiple agent instances running simultaneously.

## Diagnostic Steps

### 1. Basic Checks
1. Verify API keys are set correctly: `echo $GROQ_API_KEY` (Linux/MacOS) or `echo %GROQ_API_KEY%` (Windows)
2. Check if the agent can connect to API providers by testing with a simple query
3. Verify you're running the latest version of the agent

### 2. Server Status Checks
1. Use `/mcp` to see which servers are available and running
2. Test each server individually to identify which ones are working
3. Check server console outputs for error messages

### 3. Configuration Verification
1. Review settings.json to ensure server configurations are correct
2. Check environment variables with `env` (Linux/MacOS) or `set` (Windows)
3. Verify workspace configuration and file permissions

## Getting Help

### When to Seek Help
- After trying all troubleshooting steps in this guide
- When encountering errors not covered in this guide
- When experiencing security-related issues

### Resources
- **Documentation**: Check the full documentation in the `docs/` directory
- **Issue tracking**: Report bugs and issues through the project's issue tracker
- **Community**: Seek help from the community if available

### Information to Include When Reporting Issues
- Agent version and Python version
- Operating system and terminal being used
- Exact error messages and steps to reproduce
- Relevant configuration files (without sensitive information)
- Console output and logs (with sensitive information removed)

## Preventive Measures

### Best Practices for Avoiding Issues
- Keep environment variables secure and backed up
- Regularly update the agent to get the latest bug fixes
- Monitor API usage to avoid hitting rate limits
- Use virtual environments to avoid dependency conflicts
- Regularly review and update security policies

## Support

If you've tried all troubleshooting steps and still encounter issues, please provide detailed information about the problem when seeking support. This includes error messages, steps taken, and your environment information while protecting any sensitive data.