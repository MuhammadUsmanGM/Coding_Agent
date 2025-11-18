# Dashboard Component Documentation

## Overview
The `dashboard.py` file implements a real-time dashboard that provides insights into code quality, test coverage, security status, and other project metrics. It presents information in a visual format to help users monitor their project's health.

## Key Classes and Functions

### Dashboard Class
- **Purpose**: Creates and manages the real-time code quality dashboard
- **Key Responsibilities**:
  - Collects project metrics from various sources
  - Aggregates code quality information
  - Displays metrics in a visual format
  - Provides real-time updates on project status
  - Integrates with security and testing tools

### Dashboard Features
- Code quality metrics visualization
- Test coverage statistics
- Security vulnerability status
- Performance metrics
- Project activity indicators
- Configuration health checks

## Key Methods
- `__init__(self, agent)` - Initializes dashboard with access to agent
- `generate_dashboard_data(self)` - Collects and processes dashboard metrics
- `display_dashboard(self)` - Displays the dashboard to the user
- `update_metrics(self)` - Updates dashboard metrics in real-time
- `get_code_quality_report(self)` - Gets detailed code quality information
- `get_security_report(self)` - Gets security status information

## Data Sources
- Code analysis tools
- Test framework results
- Security scanning results
- Project configuration status
- Agent activity logs
- Performance monitoring tools

## Dependencies
- `rich` - For rich terminal dashboard display
- `agent` - Access to agent functionality and metrics
- `refactor_server` - For code quality metrics
- `security_manager` - For security status
- `testing_server` - For test coverage data
- `logger` - For dashboard activity logging

## Usage Context
This component is used when the agent needs to provide an overview of the project's health and status. It's accessed through the `/dashboard` command in the CLI, giving users a quick visual summary of various project metrics.