# Configuration Manager Server

## Overview
The Configuration Manager Server provides an interactive tool for managing configuration and credentials in various formats (.env, YAML, TOML, JSON). It allows for reading, writing, and updating configuration files through a secure API. It runs on port 10700.

## Key Features

### Multi-Format Support
- .env files for environment variables
- YAML files for structured configurations
- TOML files for modern configuration formats
- JSON files for standard structured data

### Configuration Operations
- View existing configuration values
- Save new configurations
- Update specific settings
- List available configuration files

### Secure Storage
- Stores configurations locally only
- No external transmission of sensitive data
- Validates file paths to prevent directory traversal

## API Endpoints

### POST /config
Perform configuration management operations.

**Request:**
```json
{
  "action": "view",  // "view", "save", "update", or "list"
  "config_type": "env"  // "env", "yaml", "yml", "toml", or "json"
}
```

### View Configuration
**Request:**
```json
{
  "action": "view",
  "config_type": "env"
}
```

**Response:**
```json
{
  "success": true,
  "config_type": "env",
  "data": {
    "API_KEY": "abc123",
    "DEBUG": "True"
  }
}
```

### Save Configuration
**Request:**
```json
{
  "action": "save",
  "config_type": "json",
  "data": {
    "database": {
      "host": "localhost",
      "port": 5432
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "JSON configuration saved to config/config.json"
}
```

### Update Specific Setting
**Request:**
```json
{
  "action": "update",
  "config_type": "env",
  "key": "NEW_VAR",
  "value": "new_value"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Environment variables saved to config/.env"
}
```

### List Available Configs
**Request:**
```json
{
  "action": "list"
}
```

**Response:**
```json
{
  "success": true,
  "configs": {
    "env": {
      "exists": true,
      "path": "config/.env",
      "size": 128
    },
    "json": {
      "exists": false,
      "path": "config/config.json",
      "size": 0
    }
  }
}
```

## Response Structure

### Success Responses
- `success`: Boolean indicating if the operation was successful
- Additional fields vary by action type

### Error Responses
- `success`: Boolean indicating failure
- `error`: Description of the error that occurred

## Usage Examples

### Reading Environment Variables
```python
import requests

response = requests.post('http://localhost:10700/config', json={
    'action': 'view',
    'config_type': 'env'
})

result = response.json()
if result['success']:
    config_data = result['data']
    print("Environment variables:")
    for key, value in config_data.items():
        print(f"  {key} = {value}")
else:
    print(f"Error: {result['error']}")
```

### Updating a Specific Setting
```python
import requests

response = requests.post('http://localhost:10700/config', json={
    'action': 'update',
    'config_type': 'env',
    'key': 'DATABASE_URL',
    'value': 'postgresql://localhost/mydb'
})

result = response.json()
if result['success']:
    print(result['message'])
else:
    print(f"Error: {result['error']}")
```

### Saving JSON Configuration
```python
import requests

config_data = {
    "app": {
        "name": "MyApp",
        "version": "1.0.0"
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp_db"
    }
}

response = requests.post('http://localhost:10700/config', json={
    'action': 'save',
    'config_type': 'json',
    'data': config_data
})

result = response.json()
if result['success']:
    print("Configuration saved successfully")
else:
    print(f"Error: {result['error']}")
```

## Configuration File Locations

The server manages configuration files in a `config` directory by default:
- .env: `config/.env`
- YAML: `config/config.yaml`
- TOML: `config/config.toml`
- JSON: `config/config.json`

## Implementation Notes

### Default File Creation
When a configuration file doesn't exist, the server creates a default empty file in the appropriate format to ensure subsequent read operations succeed.

### Format Conversion
The server maintains data integrity when converting between formats, though complex nested structures might lose some format-specific features.

## Security Considerations
- Only operates on local configuration files in the designated config directory
- Validates file paths to prevent directory traversal
- Does not transmit sensitive configuration data over networks
- Stores API keys and other sensitive data only locally

## Error Handling
- 400: When required parameters are missing for update actions
- 500: For file system errors or other unexpected server errors during config operations