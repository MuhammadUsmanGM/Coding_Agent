# Logger Component Documentation

## Overview
The `logger.py` file implements a comprehensive logging system for the Codeius AI agent, providing detailed logging of agent activities, user interactions, and system events for debugging and monitoring purposes.

## Key Classes and Functions

### AgentLogger Class
- **Purpose**: Centralized logging system for the AI agent
- **Key Responsibilities**:
  - Logs agent activities and responses
  - Records user interactions and queries
  - Tracks system events and errors
  - Manages log file rotation and storage
  - Formats log entries with consistent structure

### Log Features
- Structured logging with JSON format
- Multiple log levels (DEBUG, INFO, WARNING, ERROR)
- Log file rotation to manage disk space
- Sensitive information filtering
- Performance-related logging

## Key Methods
- `__init__(self, log_dir='logs', log_level='INFO')` - Initializes the logger
- `log_agent_activity(self, user_input, agent_response, actions_taken)` - Logs agent interaction
- `log_error(self, error_message, context=None)` - Logs errors with context
- `log_info(self, message, extra_data=None)` - Logs informational messages
- `log_performance(self, operation, duration, metadata)` - Logs performance metrics

## Log Structure
- Timestamp for each log entry
- Log level indication
- Component identifier
- User input and agent response
- Action details and metadata
- Performance metrics

## Dependencies
- `logging` - Python's built-in logging module
- `os` and `pathlib` - For log file management
- `json` - For structured log formatting
- `config` - For logging configuration

## Usage Context
This component is used throughout the application to maintain detailed logs of all activities, which are essential for debugging issues, monitoring performance, and analyzing usage patterns. It's integrated into the main agent, action executor, and other core components.