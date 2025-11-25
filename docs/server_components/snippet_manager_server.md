# Snippet Manager Server

## Overview
The Snippet Manager Server stores, retrieves, and manages code snippets and templates. It allows users to save commonly used code blocks, boilerplate code, and templates for rapid insertion into projects. It runs on port 10500.

## Key Features

### Snippet Management
- Save code snippets with unique keys for quick retrieval
- Retrieve saved snippets by their keys
- List all available snippet keys
- Delete snippets when no longer needed

### Format Support
- Primary storage in JSON format
- Support for YAML and other formats (future enhancement)
- Organizes snippets in a dedicated directory

### Persistent Storage
- Stores snippets in local files
- Maintains snippets between sessions
- Tracks last updated timestamps for snippets

## API Endpoints

### POST /snippet
Perform operations on snippets.

**Request:**
```json
{
  "action": "get",  // "get", "save", "delete", or "list"
  "key": "python_decorator"
}
```

### Save Snippet
**Request:**
```json
{
  "action": "save",
  "key": "python_decorator",
  "content": "@property\ndef name(self):\n    return self._name",
  "description": "Python property decorator example"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Snippet 'python_decorator' saved successfully"
}
```

### Get Snippet
**Request:**
```json
{
  "action": "get",
  "key": "python_decorator"
}
```

**Response:**
```json
{
  "success": true,
  "key": "python_decorator",
  "content": "@property\ndef name(self):\n    return self._name"
}
```

### List Snippets
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
  "snippets": ["python_decorator", "try_except_block", "flask_route"]
}
```

### Delete Snippet
**Request:**
```json
{
  "action": "delete",
  "key": "python_decorator"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Snippet 'python_decorator' deleted successfully"
}
```

## Response Structure

### Success Responses
- `success`: Boolean indicating if the operation was successful
- Additional fields depend on the specific action

### Error Responses
- `success`: Boolean indicating failure
- `error`: Description of the error that occurred

## Usage Examples

### Saving a Snippet
```python
import requests

response = requests.post('http://localhost:10500/snippet', json={
    'action': 'save',
    'key': 'python_decorator',
    'content': '@property\ndef name(self):\n    return self._name',
    'description': 'Python property decorator example'
})

result = response.json()
if result['success']:
    print(result['message'])
else:
    print(f"Error: {result['error']}")
```

### Retrieving a Snippet
```python
import requests

response = requests.post('http://localhost:10500/snippet', json={
    'action': 'get',
    'key': 'python_decorator'
})

result = response.json()
if result['success']:
    print(f"Snippet '{result['key']}':")
    print(result['content'])
else:
    print(f"Error: {result['error']}")
```

### Listing All Snippets
```python
import requests

response = requests.post('http://localhost:10500/snippet', json={
    'action': 'list'
})

result = response.json()
print(f"Available snippets: {result['snippets']}")
```

## Storage Location
- Snippets are stored in a `snippets` directory by default
- The primary storage file is `snippets.json`
- Additional formats may be supported in the future

## Implementation Notes

### File Management
The server creates the snippets directory and initializes storage files if they don't exist. All operations are persisted to the JSON file.

### Content Format
Snippets preserve formatting, including indentation and line breaks, making them suitable for code templates and complex text blocks.

## Security Considerations
- Only operates on local files in the designated snippets directory
- No external network connections
- Validates snippet keys to prevent path traversal

## Error Handling
- 400: When required parameters are missing or invalid
- 404: When trying to retrieve a non-existent snippet
- 500: For file system errors or other unexpected server errors