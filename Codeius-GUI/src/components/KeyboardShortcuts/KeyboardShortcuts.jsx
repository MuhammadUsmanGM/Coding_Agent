import React, { useEffect } from 'react';
import './KeyboardShortcuts.css';

const KeyboardShortcuts = ({ isOpen, onClose }) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const shortcuts = [
    { keys: ['Ctrl', '/'], description: 'Show/hide keyboard shortcuts' },
    { keys: ['Ctrl', 'L'], description: 'Clear conversation history' },
    { keys: ['Ctrl', 'K'], description: 'Focus on input field' },
    { keys: ['Enter'], description: 'Send message' },
    { keys: ['Shift', 'Enter'], description: 'New line in message' },
    { keys: ['Esc'], description: 'Close modals/autocomplete' },
    { keys: ['↑', '↓'], description: 'Navigate autocomplete' },
    { keys: ['/', 'command'], description: 'Trigger command autocomplete' },
  ];

  return (
    <>
      <div className="shortcuts-overlay" onClick={onClose} />
      <div className="shortcuts-modal">
        <div className="shortcuts-header">
          <h2>⌨️ Keyboard Shortcuts</h2>
          <button className="shortcuts-close" onClick={onClose}>×</button>
        </div>
        <div className="shortcuts-content">
          {shortcuts.map((shortcut, index) => (
            <div key={index} className="shortcut-item">
              <div className="shortcut-keys">
                {shortcut.keys.map((key, i) => (
                  <React.Fragment key={i}>
                    <kbd className="key">{key}</kbd>
                    {i < shortcut.keys.length - 1 && <span className="key-separator">+</span>}
                  </React.Fragment>
                ))}
              </div>
              <div className="shortcut-description">{shortcut.description}</div>
            </div>
          ))}
        </div>
        <div className="shortcuts-footer">
          Press <kbd className="key">Esc</kbd> to close
        </div>
      </div>
    </>
  );
};

export default KeyboardShortcuts;
