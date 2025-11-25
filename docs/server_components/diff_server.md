# Diff Server

## Overview
The Diff Server provides file and directory comparison capabilities using Python's difflib. It can compare content of two files or directories and return the differences in a structured format. It runs on port 10000.

## Key Features

### File Comparison
- Compare the content of two text files
- Generate unified diff output showing differences
- Identify if files are identical

### Directory Comparison
- Compare two directories and their contents
- Identify files that exist in one directory but not the other
- Show file-level differences for files present in both directories
- Provide a summary of differences between directories

### Safe File Access
- Validates that file paths exist before attempting comparison
- Reads files with utf-8 encoding with error handling
- Handles binary files gracefully by ignoring them

## API Endpoints

### POST /diff
Compare two files or directories.

**Request for files:**
```json
{
  "file1": "src/file1.py",
  "file2": "src/file2.py"
}
```

**Request for directories:**
```json
{
  "file1": "project_old/",
  "file2": "project_new/"
}
```

**Response for files:**
```json
{
  "type": "file",
  "same": false,
  "diff": [
    "Line 1: Content here",
    "Line 2: -Old content",
    "Line 2: +New content"
  ]
}
```

**Response for directories:**
```json
{
  "type": "directory",
  "same": false,
  "diff_files": ["main.py", "utils.py"],
  "only_in_first": ["old_module.py"],
  "only_in_second": ["new_module.py"],
  "file_diffs": {
    "main.py": [
      // Diff lines similar to file comparison
    ]
  }
}
```

## Response Structure

### File Comparison Response
- `type`: Always "file" for file comparisons
- `same`: Boolean indicating if files are identical
- `diff`: Array of unified diff lines

### Directory Comparison Response
- `type`: Always "directory" for directory comparisons
- `same`: Boolean indicating if directories have identical content
- `diff_files`: Array of filenames that exist in both directories but have different content
- `only_in_first`: Array of filenames that exist only in the first directory
- `only_in_second`: Array of filenames that exist only in the second directory
- `file_diffs`: Object containing detailed diffs for each differing file

## Usage Examples

### Comparing Two Files
```python
import requests

response = requests.post('http://localhost:10000/diff', json={
    'file1': 'src/old_version.py',
    'file2': 'src/new_version.py'
})

result = response.json()
if result['same']:
    print("Files are identical")
else:
    print("Differences found:")
    for line in result['diff']:
        print(line)
```

### Comparing Two Directories
```python
import requests

response = requests.post('http://localhost:10000/diff', json={
    'file1': 'project_v1/',
    'file2': 'project_v2/'
})

result = response.json()
print(f"Directories identical: {result['same']}")
print(f"Files with differences: {result['diff_files']}")
print(f"Files only in first: {result['only_in_first']}")
print(f"Files only in second: {result['only_in_second']}")
```

## Error Handling
- 400: When file paths are missing or do not exist
- 500: For unexpected server errors during comparison operations
- The server handles file encoding errors gracefully and returns appropriate error messages