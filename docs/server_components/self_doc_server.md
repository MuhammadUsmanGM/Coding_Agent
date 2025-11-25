# Self-Documenting Server

## Overview
The Self-Documenting Server automatically updates documentation files in your repository as code changes, enabling "live" updates to documents like AUTHORS, CHANGELOG, and README files. It runs on port 10300.

## Key Features

### AUTHORS File Management
- Updates the AUTHORS file with project contributors
- Automatically formats the contributors list
- Maintains standard headers and structure

### CHANGELOG Management
- Updates the CHANGELOG file with recent changes
- Maintains proper CHANGELOG format with dates
- Preserves existing entries while adding new ones

### README Section Updates
- Updates specific sections in README files
- Identifies sections by heading level
- Preserves the rest of the document content

### Offline Operation
- Works entirely offline without external dependencies
- Operates on local files only
- Maintains standard markdown formatting

## API Endpoints

### POST /update_docs
Update documentation based on code changes.

**Request:**
```json
{
  "action": "update_authors",  // "update_authors", "update_changelog", or "update_readme"
  "params": {
    // Parameters vary by action
  }
}
```

### Update Authors Action
**Request:**
```json
{
  "action": "update_authors",
  "params": {
    "contributors": ["John Doe", "Jane Smith"],
    "file_path": "AUTHORS.md"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "AUTHORS file updated at AUTHORS.md"
}
```

### Update Changelog Action
**Request:**
```json
{
  "action": "update_changelog",
  "params": {
    "changes": ["Fixed bug in user authentication", "Added new API endpoint"],
    "file_path": "CHANGELOG.md"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "CHANGELOG file updated at CHANGELOG.md"
}
```

### Update README Action
**Request:**
```json
{
  "action": "update_readme",
  "params": {
    "section_title": "Installation",
    "content": "To install the package, run `pip install package-name`",
    "file_path": "README.md"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "README section \"Installation\" updated at README.md"
}
```

## Response Structure

### Success Response
- `success`: Boolean indicating if the operation was successful
- `message`: Description of the action performed

### Error Response
- `success`: Boolean indicating failure
- `error`: Description of the error that occurred

## Usage Examples

### Updating AUTHORS File
```python
import requests

response = requests.post('http://localhost:10300/update_docs', json={
    'action': 'update_authors',
    'params': {
        'contributors': ['Alice Johnson', 'Bob Smith', 'Carol Davis'],
        'file_path': 'AUTHORS.md'
    }
})

result = response.json()
if result['success']:
    print(result['message'])
else:
    print(f"Error: {result['error']}")
```

### Updating CHANGELOG
```python
import requests

response = requests.post('http://localhost:10300/update_docs', json={
    'action': 'update_changelog',
    'params': {
        'changes': [
            'Added support for Python 3.12',
            'Fixed memory leak in data processing',
            'Updated documentation for new API'
        ],
        'file_path': 'CHANGELOG.md'
    }
})
```

### Updating a README Section
```python
import requests

response = requests.post('http://localhost:10300/update_docs', json={
    'action': 'update_readme',
    'params': {
        'section_title': 'Usage',
        'content': 'To use this library:\n\n```python\nfrom mylib import main\nmain()\n```',
        'file_path': 'README.md'
    }
})
```

## Implementation Notes

### File Format Detection
The server automatically detects and maintains proper formatting for different file types (AUTHORS, CHANGELOG, README).

### Section Detection
For README updates, the server identifies sections by looking for matching headings (##, ###, etc.) and updates only the content between that heading and the next heading of the same or higher level.

### Backup Considerations
For production use, consider implementing a backup mechanism before making changes to important documentation files.

## Security Considerations
- Only modifies local files in the project directory
- Validates file paths to prevent directory traversal
- Doesn't make changes outside the project root

## Error Handling
- 400: When required parameters are missing
- 500: For file system errors or other unexpected server errors