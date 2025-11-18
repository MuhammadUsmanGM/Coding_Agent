# Context Manager Component Documentation

## Overview
The `context_manager.py` file manages project context for the AI agent, including project discovery, code analysis, dependency tracking, and semantic search capabilities. It helps the agent understand the structure and content of the current project.

## Key Classes and Functions

### ContextManager Class
- **Purpose**: Manages project context information for the AI agent
- **Key Responsibilities**:
  - Discovers and analyzes project structure
  - Tracks project files and dependencies
  - Provides semantic search within the project
  - Maintains project metadata and configuration
  - Identifies relevant files for specific tasks

### Context Features
- Project structure analysis
- File type identification
- Dependency mapping
- Semantic code search
- Context summarization
- Cross-reference tracking

## Key Methods
- `__init__(self, workspace_path='.')` - Initializes with workspace path
- `analyze_project_structure(self)` - Analyzes the project structure
- `find_relevant_files(self, query, max_results=10)` - Finds files related to a query
- `semantic_search(self, query)` - Performs semantic search across codebase
- `get_file_context(self, file_path)` - Gets context information for a specific file
- `generate_context_summary(self)` - Creates a summary of project context
- `auto_detect_project_type(self)` - Detects project type and framework

## Search Capabilities
- Function name searching
- Class name searching
- TODO/FIXME comment searching
- Cross-reference analysis
- Code pattern matching

## Dependencies
- `os` and `pathlib` - For file system operations
- `language_detector` - For identifying file languages
- `code_analyzer` - For code analysis
- `config` - For context configuration
- `logger` - For logging context operations

## Usage Context
This component is used when the agent needs to understand the current project, find relevant files, perform code searches, or maintain awareness of the project structure. It's integrated with commands like `/context`, `/search`, `/find_function`, etc.