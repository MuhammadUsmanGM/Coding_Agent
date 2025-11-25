# Database Server

## Overview
The Database Server provides safe access to local SQLite databases, allowing SQL queries while implementing security measures to prevent dangerous operations. It runs on port 9700.

## Key Features

### Safe SQL Execution
- Executes queries only on local SQLite files
- Validates database paths to ensure they're within the allowed directory
- Implements basic SQL validation to prevent dangerous operations
- Returns structured results with column names and data

### Security Measures
- Path validation to ensure database files are within the current directory
- Blocking of potentially dangerous SQL operations (DROP, DELETE, etc.)
- Optional confirmation for operations that might modify data

## API Endpoints

### POST /query
Execute SQL queries on a local SQLite database.

**Request:**
```json
{
  "sql": "SELECT * FROM users WHERE active = 1",
  "db_path": "data.db",  // Optional, defaults to 'data.db'
  "confirm_dangerous": false  // Required for dangerous operations
}
```

**Response:**
```json
{
  "columns": ["id", "name", "email", "active"],
  "rows": [
    [1, "John Doe", "john@example.com", 1],
    [2, "Jane Smith", "jane@example.com", 1]
  ]
}
```

## Security Considerations

### Path Validation
The server validates that database paths are within the current working directory to prevent access to sensitive files outside the project.

### SQL Operation Validation
Currently blocks potentially dangerous operations like DROP statements. The implementation can be expanded to include validation for other operations.

### Dangerous Operations
Certain SQL operations (currently DROP and DELETE) require explicit confirmation via the `confirm_dangerous` parameter to prevent accidental data loss.

## Usage Examples

### Basic Query
```python
import requests

response = requests.post('http://localhost:9700/query', json={
    'sql': 'SELECT * FROM users LIMIT 5'
})

result = response.json()
print(f"Columns: {result['columns']}")
print(f"Rows: {result['rows']}")
```

### Query with Custom Database Path
```python
import requests

response = requests.post('http://localhost:9700/query', json={
    'sql': 'SELECT COUNT(*) FROM users',
    'db_path': './databases/app.db'
})
```

### Performing an Update (with confirmation)
```python
import requests

response = requests.post('http://localhost:9700/query', json={
    'sql': 'UPDATE users SET active = 0 WHERE last_login < "2023-01-01"',
    'confirm_dangerous': True
})
```

## Error Handling
The server returns appropriate HTTP status codes and error messages for various failure scenarios:
- 400: Invalid request parameters or dangerous operation without confirmation
- 500: Unexpected server errors
- Database-specific errors are returned in the response body