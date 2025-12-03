# Git Controls Component

## Overview
The Git Controls component provides a GUI for version control operations. It allows users to perform common Git operations directly from the GUI without needing to use the command line.

## Purpose
This component replaces browser alerts with a professional interface for Git operations such as:
- Checking repository status
- Adding files to staging
- Committing changes
- Pushing and pulling from remote repositories
- Cloning repositories
- Managing branches

## Location and Integration
- **File**: `src/components/GitControls/GitControls.jsx`
- **CSS**: `src/components/GitControls/GitControls.css`
- **Integration**: Added to the main App component below the Navbar
- **Positioning**: Positioned absolutely at 95px from the top to be below the Navbar

## Features
1. **Status Indicator**
   - Displays current repository status
   - Updates on demand when clicked
   - Shows loading state during operations

2. **Operation Buttons**
   - Add button: Adds files to Git staging area
   - Commit button: Commits staged changes (opens commit dialog)
   - Push button: Pushes changes to remote repository
   - Pull button: Pulls changes from remote repository
   - More button: Opens dropdown with additional operations

3. **Dropdown Menu** (Behind the more button)
   - Clone repository
   - Create branch
   - Switch branch
   - View commit log
   - Manage remotes
   - Initialize new repository

4. **Professional UI Elements**
   - Modern button design with hover effects
   - Glassmorphism styling
   - Dark theme consistent with application
   - Responsive design
   - Icons for visual recognition

## Technical Implementation

### API Integration
The Git Controls component communicates with the Git MCP server:
- GET `/api/git/status` - Check repository status
- POST `/api/git/add` - Add files to staging
- POST `/api/git/commit` - Commit changes
- POST `/api/git/push` - Push changes
- POST `/api/git/pull` - Pull changes
- POST `/api/git/clone` - Clone repository
- POST `/api/git/branch` - Manage branches
- GET `/api/git/log` - View commit history

### Confirmation System
- Uses ConfirmationDialog component instead of browser confirm()
- Professional styling with appropriate warning indicators
- Type-specific styling for different operations

### Notification System
- Uses Toast system for all notifications
- Success messages for completed operations
- Error messages for failed operations
- Consistent with overall application styling

## User Experience
- Minimal visual footprint when not in use
- Intuitive button layout with recognizable icons
- Immediate feedback for operations
- Professional appearance with dark theme
- Responsive behavior for different screen sizes
- No disruption to main workflow

## Security Considerations
- All Git operations are validated server-side
- Path validation to prevent directory traversal
- Rate limiting on operations
- Input sanitization for all user-provided parameters
- Confirmation dialogs for potentially destructive operations

## Responsive Design
- Adapts to smaller screens
- Button labels hide on mobile to preserve space
- Maintains usability on all device sizes
- Proper touch targets for mobile devices

## Future Enhancements
- Visual indication of current branch
- Uncommitted changes counter
- Integration with multiple remotes
- Git graph visualization
- Stash operations
- Tag management
- Merge conflict resolution interface