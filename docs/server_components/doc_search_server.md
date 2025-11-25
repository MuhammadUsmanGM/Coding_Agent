# Documentation Search Server

## Overview
The Documentation Search Server provides local documentation search capabilities by finding and extracting information from .md, .txt, and .rst files. It runs on port 9600 and uses asynchronous file processing for efficient searching.

## Key Features

### File Format Support
- Markdown (.md) files
- Text (.txt) files
- reStructuredText (.rst) files
- Extensible to support additional formats

### Asynchronous Processing
- Uses asyncio and aiofiles for efficient file processing
- Avoids blocking during file I/O operations
- Handles large documentation sets efficiently

### Content Extraction
- Searches for query terms in documentation files
- Returns matching lines with context
- Limits line length to prevent very long results
- Provides file paths and line numbers for matches

## API Endpoints

### GET /doc_search
Search for content in documentation files.

**Parameters:**
- `q`: Query term to search for (required)
- `root`: Root directory to search in (optional, defaults to server's configured root)

**Response:**
```json
[
  {
    "file": "docs/guide.md",
    "line": 15,
    "match": "This is a documentation entry about the guide feature..."
  },
  {
    "file": "README.txt",
    "line": 8,
    "match": "Quick start guide included..."
  }
]
```

## Response Structure

Each result in the response array contains:
- `file`: Relative path to the file containing the match
- `line`: Line number where the query term was found
- `match`: The matching line content (truncated to 200 characters)

### Limitations
- Maximum of 20 results per file
- Maximum of 50 total results returned
- Match lines are limited to 200 characters
- Case-insensitive search by default

## Usage Examples

### Searching Documentation
```python
import requests

response = requests.get('http://localhost:9600/doc_search', params={
    'q': 'configuration',
    'root': '/path/to/docs'
})

results = response.json()
for result in results:
    print(f"Found in {result['file']} line {result['line']}: {result['match']}")
```

### Finding Specific Terms
```python
import requests

search_term = "installation"
response = requests.get('http://localhost:9600/doc_search', params={
    'q': search_term
})

docs = response.json()
print(f"Found {len(docs)} occurrences of '{search_term}':")
for doc in docs:
    print(f"  - {doc['file']}:{doc['line']} - {doc['match']}")
```

## Implementation Notes

### Asynchronous Processing
The server uses asyncio and aiofiles to efficiently process documentation files without blocking. This allows it to search through large documentation sets more efficiently.

### Case-Insensitive Search
All searches are performed in a case-insensitive manner by converting the query and file content to lowercase before matching.

### File Access
The server only searches within the specified root directory and its subdirectories, preventing access to files outside the intended documentation set.

## Security Considerations
- Only searches files within the specified root directory
- Processes only readable text files
- No code execution, only text pattern matching in documentation content
- Limits file path traversal to prevent access to sensitive files

## Error Handling
- 400: When no query term is provided
- 500: For server-side errors during file processing