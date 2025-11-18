# Model Manager Component Documentation

## Overview
The `model_manager.py` file handles the management of different LLM providers, model switching, and provides a unified interface for interacting with various AI models. It supports multiple providers and enables seamless switching between them.

## Key Classes and Functions

### ModelManager Class
- **Purpose**: Manages multiple LLM providers and model switching
- **Key Responsibilities**:
  - Initializes and maintains connections to different LLM providers
  - Handles model switching based on user commands
  - Provides a unified interface for all LLM interactions
  - Manages provider configurations and credentials
  - Implements fallback mechanisms between providers

### Supported Providers
- Groq (Llama models)
- Google (Gemini models)
- Custom OpenAI-compatible APIs
- MCP (Model Context Protocol) providers

## Key Methods
- `__init__(self, config)` - Initializes the manager with configuration
- `get_completion(self, messages, model_key=None)` - Gets completion from active provider
- `switch_model(self, model_key)` - Switches to a specific model
- `get_available_models(self)` - Returns list of available models
- `add_custom_model(self, name, api_key, base_url, model_id)` - Adds a custom model

## Dependencies
- `provider` modules - Various LLM provider implementations
- `config` - For configuration management
- `logger` - For logging model switches and completions
- `error_handler` - For handling model-related errors

## Usage Context
This component is used by the main agent to abstract away the complexity of dealing with different LLM providers, allowing the agent to work with any supported model through a consistent interface.