# CLI Component Documentation

## Overview
The `cli.py` file contains the command-line interface implementation with rich visuals, input handling, and user interaction management. It provides the main interface for users to interact with the AI coding agent.

## Key Features

### Visual Interface
- Rich terminal interface with colorful panels and elements
- Bordered input field with heavy border styling for better UX
- Mode indicators (interaction vs shell mode)
- Welcome and status panels with visual feedback

### Command Handling
- Implements numerous commands like `/models`, `/mcp`, `/shell`, `/toggle`, etc.
- Command completion using prompt_toolkit
- Mode switching functionality
- Help and documentation commands

### Input Management
- Enhanced input prompt with visual styling
- Multi-column command completion
- Support for special keys and navigation
- Mode-specific styling (cyan for interaction, orange for shell)

## Key Classes and Functions

### Main Execution Loop
- `main()` - Main entry point for the CLI application
- Handles agent initialization and main interaction loop
- Manages mode switching between interaction and shell modes

### Command Handlers
- Various functions to handle different commands
- Integration with agent's functionality
- Visual feedback for command execution

## Dependencies
- `rich` - For rich terminal UI elements
- `prompt_toolkit` - For advanced input handling and completion
- `agent` - Main agent functionality
- `dashboard` - For dashboard commands
- `context_manager` - For context-related commands
- `security_cli` - For security-related commands

## Usage Context
This is the main user interface component, providing the terminal-based interaction layer between users and the AI coding agent. It handles all user inputs and displays agent responses with rich visual formatting.