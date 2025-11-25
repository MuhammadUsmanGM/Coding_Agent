# Automation Server

## Overview
The Automation Server handles script and form automation tasks, enabling repetitive coding chores like batch renaming variables, auto-generating project scaffolds, and managing environment files with templates. It runs on port 10100.

## Key Features

### Project Scaffolding
- Generate project structures based on templates (python, web, basic)
- Creates appropriate directory structure and initial files for different project types
- Supports customizable options for project generation

### Environment File Management
- Create and update `.env` files with templates
- Supports both creation of new environment files and updating existing ones
- Preserves existing variables when updating files

### Variable Renaming
- Batch rename variables across files
- Uses regex with word boundaries to avoid partial matches
- Updates all occurrences of a variable name in specified files

## API Endpoints

### POST /scaffold
Generate project scaffolding based on templates.

**Request:**
```json
{
  "template": "python",  // "python", "web", or "basic"
  "project_name": "my_project",
  "options": {}
}
```

**Response:**
```json
{
  "success": true,
  "message": "Project my_project created successfully",
  "path": "/path/to/my_project",
  "template": "python"
}
```

### POST /env
Manage environment files.

**Request:**
```json
{
  "action": "create",  // "create" or "update"
  "template": "default",
  "output_file": ".env",
  "variables": {
    "API_KEY": "abc123",
    "DEBUG": "True"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Environment file .env created successfully",
  "path": "/absolute/path/to/.env"
}
```

### POST /rename
Batch rename variables in files.

**Request:**
```json
{
  "file_path": "src/example.py",
  "old_name": "old_variable",
  "new_name": "new_variable_name"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Variable renamed from old_variable to new_variable_name in src/example.py",
  "replacements": 5
}
```

## Usage Examples

### Creating a Python Project
```python
import requests

response = requests.post('http://localhost:10100/scaffold', json={
    'template': 'python',
    'project_name': 'my_new_project'
})

result = response.json()
print(result['message'])
```

### Managing Environment Variables
```python
import requests

response = requests.post('http://localhost:10100/env', json={
    'action': 'create',
    'variables': {
        'DATABASE_URL': 'postgresql://localhost/mydb',
        'DEBUG': 'True'
    }
})
```