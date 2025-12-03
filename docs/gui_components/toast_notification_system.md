# Toast and Notification System

## Overview
The Toast system provides beautiful, professional notifications as an alternative to browser alerts. It replaces all intrusive alerts with elegant, unobtrusive notifications that match the application's dark theme.

## Components

### 1. Toast Component
- **File**: `src/components/Toast/Toast.jsx`
- **Purpose**: Individual notification element with customizable content and appearance
- **Props**:
  - `message`: Text content of the toast
  - `type`: Type of toast ('info', 'success', 'warning', 'error')
  - `duration`: Auto-dismiss duration in milliseconds
  - `onClose`: Callback function when toast is dismissed
- **Features**:
  - Animated appearance/disappearance
  - Type-specific icons and colors
  - Auto-dismiss with customizable duration
  - Manual dismiss option
  - Close button for immediate dismissal

### 2. Toast Container
- **File**: `src/components/Toast/ToastContainer.jsx`
- **Purpose**: Manages multiple toasts and provides context for the entire app
- **Features**:
  - Centralized toast management
  - React Context API for global access
  - Automatic cleanup of dismissed toasts
  - Stacking of multiple toasts
  - Z-index management to stay on top of other elements

### 3. Confirmation Dialog Component
- **File**: `src/components/ConfirmationDialog/ConfirmationDialog.jsx`
- **Purpose**: Professional confirmation UI instead of browser confirm dialogs
- **Props**:
  - `isOpen`: Whether dialog is visible
  - `onClose`: Callback when dialog is closed
  - `onConfirm`: Callback when user confirms
  - `title`: Dialog title
  - `message`: Confirmation message
  - `confirmText`: Text for confirm button
  - `cancelText`: Text for cancel button
  - `type`: Dialog type ('warning', 'danger', 'info')
- **Features**:
  - Smooth animations
  - Type-specific styling
  - Backdrop click to close
  - Escape key to cancel
  - Accessible design

### 4. Toast Hook
- **File**: `src/components/Toast/ToastContainer.jsx` (useToast hook)
- **Purpose**: Hook for accessing toast functionality throughout the application
- **Usage**:
  ```javascript
  const toast = useToast();
  toast.success('Operation completed successfully');
  toast.error('An error occurred');
  toast.warning('This is a warning');
  toast.info('Additional information');
  ```

## Implementation
The toast system has replaced all browser alerts throughout the application:
- Git operation notifications
- Error messages
- Success confirmations
- Warning messages
- System status notifications

All notifications now appear as elegant toasts in the top-right corner of the screen with appropriate styling based on their type.

## Styling
- Dark-themed to match the application
- Glassmorphism effect with backdrop blur
- Smooth slide-in/slide-out animations
- Type-specific colors and icons
- Responsive design that works on all screen sizes

## Benefits Over Browser Alerts
- Better user experience with non-intrusive notifications
- Consistent styling matching the application theme
- Multiple simultaneous notifications
- Automatic dismissal
- Better accessibility
- No interruption of user workflow
- Professional appearance