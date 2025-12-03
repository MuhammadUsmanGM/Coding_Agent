# GUI Components Documentation

## Overview
The Codeius GUI is a modern React-based interface that provides a rich visual experience for interacting with the AI coding agent. It consists of multiple React components that work together to create a cohesive and functional interface.

## Key Components

### 1. GitControls Component
- **File**: `src/components/GitControls/GitControls.jsx`
- **Purpose**: Provides Git version control operations through the GUI
- **Features**:
  - Status indicator showing repository state
  - Add, commit, push, pull operations
  - Dropdown menu for additional operations (clone, branch management, etc.)
  - Professional notification system with toasts
  - Confirmation dialogs for destructive operations
- **Styling**: Dark-themed component with gradient backgrounds and glassmorphism effects
- **Integration**: Connects to the Git MCP server via API calls

### 2. Toast Component
- **File**: `src/components/Toast/Toast.jsx`
- **File**: `src/components/Toast/ToastContainer.jsx`
- **Purpose**: Provides beautiful notifications instead of browser alerts
- **Features**:
  - Multiple notification types (info, success, warning, error)
  - Auto-dismiss functionality
  - Manual dismiss option
  - Slide-in animations
  - Responsive design
- **Styling**: Dark-themed with glassmorphism effect to match the application theme

### 3. ConfirmationDialog Component
- **File**: `src/components/ConfirmationDialog/ConfirmationDialog.jsx`
- **Purpose**: Provides professional confirmation dialogs instead of browser confirm()
- **Features**:
  - Customizable titles and messages
  - Type-specific styling (warning, danger, info)
  - Action buttons with proper labeling
  - Backdrop click to close
  - Smooth animations
- **Styling**: Dark-themed with glassmorphism effect to match the application theme

### 4. Navbar Component
- **File**: `src/components/Navbar/Navbar.jsx`
- **Purpose**: Top navigation bar with access to settings and history
- **Features**:
  - Logo and branding
  - Settings access
  - History modal access
  - Model selection (if applicable)
- **Integration**: Connected to the Settings component and HistoryModal

### 5. Sidebar Component
- **File**: `src/components/Sidebar/Sidebar.jsx`
- **Purpose**: Left sidebar with command shortcuts and information
- **Features**:
  - Collapsible design
  - Command shortcuts with descriptions
  - System information and status
  - Toggle functionality
- **Styling**: Dark-themed with gradient backgrounds

### 6. InputField Component
- **File**: `src/components/InputField/InputField.jsx`
- **Purpose**: Main input field for interacting with the AI
- **Features**:
  - Multi-line text input
  - Command completion
  - Auto-resizing based on content
  - Character count
  - Special key combinations support
- **Integration**: Connects to backend API to submit queries

### 7. ChatBubble Component
- **File**: `src/components/ChatBubble/ChatBubble.jsx`
- **Purpose**: Displays conversation messages between user and AI
- **Features**:
  - Different styling for user vs AI messages
  - Support for Markdown rendering
  - Syntax highlighting for code blocks
  - Copy functionality for messages and code
  - Regeneration and deletion options
- **Styling**: Different styles for user and AI messages with appropriate colors

### 8. MessageActions Component
- **File**: `src/components/MessageActions/MessageActions.jsx`
- **Purpose**: Provides contextual actions for each message
- **Features**:
  - Copy message functionality
  - Regenerate response (AI messages only)
  - Delete message functionality
  - Hover activation for minimal UI impact
- **Integration**: Uses Toast system for notifications instead of alerts

### 9. HistoryModal Component
- **File**: `src/components/HistoryModal/HistoryModal.jsx`
- **Purpose**: Modal for viewing conversation history
- **Features**:
  - List of past conversations
  - Timestamps and previews
  - Deletion functionality with confirmation
  - New chat creation
- **Integration**: Uses the new ConfirmationDialog component for delete operations

### 10. KeyboardShortcuts Component
- **File**: `src/components/KeyboardShortcuts/KeyboardShortcuts.jsx`
- **Purpose**: Documentation for keyboard shortcuts
- **Features**:
  - Overlay display
  - Comprehensive shortcut list
  - Close functionality
- **Styling**: Semi-transparent overlay with dark-themed content

## GUI Architecture

### State Management
- Global state managed through React hooks (useState, useEffect, etc.)
- Context API for shared data across components
- Local state for component-specific data
- Props drilling minimised through Context API

### Styling Approach
- CSS Modules for component-scoped styles
- Dark theme with gradient accents
- Glassmorphism effects for modern look
- Responsive design for different screen sizes
- Consistent color palette throughout components

### API Integration
- Fetch API for HTTP requests
- Service layer for common operations
- Error handling with Toast notifications
- Loading states for user feedback

### Security Measures
- Input sanitization
- Cross-site scripting prevention
- Secure API communication
- Path validation for file operations

## Responsive Design
The GUI is designed to be responsive across different screen sizes:
- Mobile-first approach with media queries
- Flexible layouts that adapt to screen size
- Touch-friendly interface elements
- Adaptive text sizing

## Accessibility Features
- Semantic HTML for screen readers
- Proper focus management
- Sufficient color contrast
- Keyboard navigation support
- Alt texts for images

## Future Enhancements
- Real-time collaboration features
- Plugin system for extending UI components
- Customization options (themes, layouts)
- Offline functionality
- Voice input capabilities