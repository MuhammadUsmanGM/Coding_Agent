# Custom Model Integration Guide

## Overview

Codeius AI Coding Agent supports adding custom AI models from any OpenAI-compatible API endpoint. This allows you to connect to various providers like OpenAI, Anthropic, Azure OpenAI, or your own custom API endpoints.

## Adding a Custom Model

### Using the Agent Interface

1. Start the Codeius agent:
   ```bash
   codeius
   ```

2. Use the `/add_model` command:
   ```
   /add_model
   ```

3. Follow the prompts to provide:
   - Model name (for identification)
   - API key (securely stored)
   - Base URL (e.g., `https://api.openai.com/v1`)
   - Model ID (e.g., `gpt-4`, `claude-3-opus`, or custom model identifier)

4. The model will be available in `/models` and can be switched to with `/switch`

### Example Configuration

For OpenAI GPT-4:
- Model name: `my-openai-gpt4`
- API key: `your_openai_api_key`
- Base URL: `https://api.openai.com/v1`
- Model ID: `gpt-4`

For Azure OpenAI:
- Model name: `my-azure-model`
- API key: `your_azure_api_key`
- Base URL: `https://your-resource-name.openai.azure.com`
- Model ID: `your-deployment-name`

## Managing Custom Models

### Listing Available Models

Use the `/models` command to see all available AI models including custom ones:

```
/models
```

### Switching Models

Use the `/switch` command to change to a specific model:

```
/switch [model_name]
```

For example:
```
/switch my-openai-gpt4
```

### Listing Custom Models Only

Use `/mcp` to list available MCP servers and custom models.

## Configuration via Code

You can also add custom models programmatically:

```python
from coding_agent.agent import CodingAgent

agent = CodingAgent()
success = agent.add_custom_model(
    name="my-custom-model",
    api_key="your-api-key",
    base_url="https://api.example.com/v1",
    model="custom-model-id"
)

if success:
    print("Custom model added successfully!")
```

## Security Considerations

- API keys are stored in a local `custom_models.json` file
- The file is stored locally and not transmitted over networks
- Use appropriate file permissions to protect the configuration file
- Remove models when no longer needed using the appropriate commands

## Troubleshooting

### Common Issues

1. **Invalid API Key**: Verify that your API key is correct and has the necessary permissions
2. **Invalid Base URL**: Ensure the base URL is properly formatted and accessible
3. **Model Not Found**: Verify that the model ID exists and is accessible with your API key
4. **Connection Errors**: Check your internet connection and firewall settings

### Testing Connection

After adding a model, test that it works by asking a simple question:

```
This is a test. Respond with "Model working" only.
```

## Best Practices

- Store API keys for production use in environment variables rather than in code
- Use descriptive names for your custom models to easily identify them later
- Keep your API keys secure and never commit them to version control
- Regularly check for updates or changes in the API provider's terms of service