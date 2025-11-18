# Google LLM Provider Documentation

## Overview
The `google.py` file contains the implementation for integrating with Google's Generative AI API. It provides access to Google's Gemini models with various capabilities.

## Key Classes and Functions

### GoogleProvider Class
- **Purpose**: Handles communication with Google's Generative AI API
- **Key Responsibilities**:
  - Creates and manages API clients for Google
  - Processes chat completions requests using Gemini models
  - Handles model configuration and parameters
  - Manages API key authentication

### Key Methods
- `__init__(self, api_key, model_name)` - Initializes the provider with credentials
- `get_completion(self, messages, **kwargs)` - Gets completion from Google API
- `validate_config(self)` - Validates configuration settings
- `format_messages_for_gemini(self, messages)` - Formats messages for Gemini API

## Configuration
- Default model: `gemini-1.5-flash`
- Environment variable: `GOOGLE_API_KEY`
- Configurable via `GOOGLE_API_MODEL` environment variable

## Dependencies
- `google.generativeai` - Google's Generative AI Python client
- `pydantic` - For configuration validation
- Base provider classes from `base.py`

## Usage Context
Used by the model manager to provide Google's LLM options to the agent. This provider offers access to Gemini models with multimodal capabilities.