# Code Search Server

## Overview
The Code Search Server provides semantic search capabilities across local project files, scanning for function/class/TODO definitions and other code patterns. It runs on port 9300 and uses asynchronous file processing for efficient searching.

## Key Features

### Pattern Recognition
- Functions: Identifies function definitions using `def` keyword
- Classes: Identifies class definitions using `class` keyword
- TODOs: Identifies TODO comments in code
- Extensible pattern matching system

### Asynchronous Processing
- Uses asyncio for efficient file processing
- Asynchronously reads files to avoid blocking
- Handles multiple files concurrently

### File Filtering
- Processes only Python (.py) files
- Skips files that cannot be read (e.g., binary files)
- Searches recursively through all subdirectories

## API Endpoints

### GET /search
Search for code patterns in project files.

**Parameters:**
- `type` (optional): Type of pattern to search for (default: "function")
  - "function": Search for function definitions (`def`)
  - "class": Search for class definitions (`class`)
  - "todo": Search for TODO comments
- `root` (optional): Root directory to search in (default: server's configured root)

**Response:**
```json
[
  {
    "file": "src/example.py",
    "line": 5,
    "match": "def my_function"
  },
  {
    "file": "src/module.py",
    "line": 12,
    "match": "class MyClass"
  }
]
```

## Response Structure

Each result in the response array contains:
- `file`: Relative path to the file containing the match
- `line`: Line number where the pattern was found
- `match`: The actual matched text

## Usage Examples

### Searching for Functions
```python
import requests

response = requests.get('http://localhost:9300/search', params={
    'type': 'function',
    'root': '/path/to/project'
})

results = response.json()
for result in results:
    print(f"Found {result['match']} in {result['file']} at line {result['line']}")
```

### Searching for Classes
```python
import requests

response = requests.get('http://localhost:9300/search', params={
    'type': 'class'
})

results = response.json()
print(f"Found {len(results)} classes in the project:")
for result in results:
    print(f"  - {result['match']} ({result['file']}:{result['line']})")
```

### Searching for TODO Comments
```python
import requests

response = requests.get('http://localhost:9300/search', params={
    'type': 'todo'
})

todos = response.json()
print(f"Found {len(todos)} TODOs in the project:")
for todo in todos:
    print(f"  - {todo['match']} in {todo['file']}:{todo['line']}")
```

## Implementation Notes

### Asynchronous Processing
The server uses asyncio and aiofiles to efficiently process files without blocking. This allows it to handle large codebases more efficiently.

### Pattern Matching
The server uses regular expressions to identify patterns in the code. The patterns are defined in the PATTERNS dictionary and can be extended to support additional search types.

### File Access
The server only searches within the specified root directory and its subdirectories, preventing access to files outside the intended project.

## Security Considerations
- Only searches files within the specified root directory
- Processes only readable text files
- No code execution, only pattern matching in file contents

## Error Handling
The server follows standard HTTP error codes and typically returns JSON responses with error details:
- 400: Invalid parameters
- 500: Server-side errors during file processing