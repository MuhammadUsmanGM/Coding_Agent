# React Template Component Documentation

## Overview
The `react_template.py` file contains code generation templates for creating new React/JavaScript projects. It provides scaffolding for React applications with modern best practices and standard configurations.

## Key Classes and Functions

### ReactTemplate Class
- **Purpose**: Generates React project scaffolding and boilerplate code
- **Key Responsibilities**:
  - Creates React project structure with proper directories
  - Generates package.json with standard dependencies
  - Creates basic React component files
  - Sets up standard configurations (ESLint, Prettier, etc.)
  - Provides common React component patterns and templates

### Generated Project Structure
- `public/` directory with HTML template
- `src/` directory with React components
- `src/index.js` as entry point
- Standard React component structure
- Configuration files for build tools

## Key Methods
- `create_react_project(self, project_path, project_name)` - Main method to create a React project
- `create_package_json(self, project_path, project_name)` - Creates package.json with dependencies
- `create_src_directory(self, project_path)` - Creates source directory structure
- `create_main_component(self, project_path, project_name)` - Creates main React component
- `create_index_files(self, project_path)` - Creates index files and entry points

## Dependencies
- `os` and `pathlib` - For file and directory operations
- `json` - For generating package.json
- Standard Python file operations

## Usage Context
This component is used when generating new React projects via the `/scaffold` command or similar functionality in the agent. It provides a quick way to start new React projects with proper structure and configurations.