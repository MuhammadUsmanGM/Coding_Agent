# Task Scheduler Server

## Overview
The Task Scheduler Server provides local cron/task scheduling capabilities using the schedule library. It allows the agent to run commands, execute tests, or perform code checks automatically at specified intervals. It runs on port 10800.

## Key Features

### Task Types
- Command execution tasks (shell commands)
- Test execution tasks (pytest automation)
- Script execution tasks (custom Python scripts)
- Custom code execution tasks (inline Python code)

### Scheduling Options
- Interval-based scheduling (every X minutes/hours/days)
- Fixed time scheduling (daily at specific time)
- Day-based scheduling (weekly schedules)
- Flexible interval formats (e.g., "every 5 minutes", "daily at 10:30")

### Task Management
- Create and schedule new tasks
- List all scheduled tasks
- Remove specific tasks
- Start and stop the scheduler

### Asynchronous Execution
- Asynchronous task scheduling and execution
- Non-blocking operations using asyncio
- Thread pool execution for synchronous tasks

## API Endpoints

### POST /schedule
Manage scheduled tasks.

**Request:**
```json
{
  "action": "create"  // "start", "stop", "create", "list", or "remove"
}
```

### Starting the Scheduler
**Request:**
```json
{
  "action": "start"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Scheduler started"
}
```

### Creating a Task
**Request:**
```json
{
  "action": "create",
  "task_id": "backup_task",
  "type": "command",
  "interval": "every 1 hour",
  "command": "python backup.py"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Task 'backup_task' scheduled to run every 1 hour",
  "task_id": "backup_task",
  "next_run": "2023-10-05 14:30:00"
}
```

### Listing Tasks
**Request:**
```json
{
  "action": "list"
}
```

**Response:**
```json
{
  "status": "success",
  "tasks": [
    {
      "id": "backup_task",
      "details": {
        "type": "command",
        "interval": "every 1 hour",
        "command": "python backup.py",
        "file_path": null,
        "custom_script": null,
        "next_run": "2023-10-05 14:30:00",
        "created_at": "2023-10-05 13:00:00"
      }
    }
  ],
  "count": 1
}
```

### Removing a Task
**Request:**
```json
{
  "action": "remove",
  "task_id": "backup_task"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Task 'backup_task' removed"
}
```

## Response Structure

### Success Responses
- `status`: Status of the operation ("success", "info")
- `message`: Description of the operation result
- Additional fields depending on the specific action

### Error Responses
- `status`: "error" 
- `message`: Description of the error that occurred

## Scheduling Formats

### Interval Formats
- "every X minutes/hours/days/seconds" - e.g., "every 5 minutes"
- "hourly", "daily" - for fixed intervals
- "daily at HH:MM" - for specific daily times

### Day-Based Schedules
- "monday at HH:MM", "tuesday at HH:MM", etc.
- For weekly recurring tasks

## Task Types

### Command Tasks
Execute shell commands at scheduled intervals.

**Parameters:**
- `command`: The shell command to execute

### Test Tasks
Run pytest tests automatically.

**Parameters:**
- `file_path`: Path to test directory or specific test file (optional, defaults to current directory)

### Script Tasks
Execute Python scripts at scheduled times.

**Parameters:**
- `file_path`: Path to the Python script to execute

### Custom Tasks
Execute inline Python code.

**Parameters:**
- `custom_script`: The Python code to execute

## Usage Examples

### Scheduling a Command Task
```python
import requests

response = requests.post('http://localhost:10800/schedule', json={
    'action': 'create',
    'task_id': 'backup_task',
    'type': 'command',
    'interval': 'daily at 2:00',
    'command': 'tar -czf backup.tar.gz /path/to/data'
})

result = response.json()
if result['status'] == 'success':
    print(result['message'])
    print(f"Next run: {result['next_run']}")
else:
    print(f"Error: {result['message']}")
```

### Scheduling Test Execution
```python
import requests

response = requests.post('http://localhost:10800/schedule', json={
    'action': 'create',
    'task_id': 'test_runner',
    'type': 'test',
    'interval': 'every 2 hours',
    'file_path': './tests/'
})

result = response.json()
print(f"Test runner scheduled: {result['message']}")
```

### Starting the Scheduler and Listing Tasks
```python
import requests

# Start the scheduler
start_response = requests.post('http://localhost:10800/schedule', json={
    'action': 'start'
})

if start_response.json()['status'] == 'success':
    # List all scheduled tasks
    list_response = requests.post('http://localhost:10800/schedule', json={
        'action': 'list'
    })
    
    tasks_data = list_response.json()
    print(f"Scheduled {tasks_data['count']} tasks:")
    for task in tasks_data['tasks']:
        print(f"  - {task['id']}: {task['details']['type']} at {task['details']['interval']}")
```

## Implementation Notes

### Event Loop Management
The server manages its own asyncio event loop to handle scheduled tasks asynchronously while integrating with the Flask framework.

### Task Persistence
Tasks are stored in memory and will be lost when the server restarts. Implementations requiring persistent scheduling should add database storage for task definitions.

### Threading Considerations
The server uses thread-safe operations to manage the schedule from multiple threads where necessary.

## Security Considerations
- Only executes commands within the current project or allowed directories
- No remote code execution capabilities
- Rate limiting and resource management
- Input validation for command parameters

## Error Handling
- 400: When required parameters are missing or invalid
- 500: For scheduling errors or other server-side issues during task management