import React, { useState } from 'react';
import { useToast } from '../Toast/ToastContainer';
import './MessageActions.css';

const MessageActions = ({ message, onCopy, onRegenerate, onDelete, onEdit }) => {
  const [showActions, setShowActions] = useState(false);
  const [copied, setCopied] = useState(false);
  const toast = useToast();

  const handleCopy = () => {
    onCopy(message.text);
    setCopied(true);
    toast.success('Message copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCopyResponse = () => {
    navigator.clipboard.writeText(message.text);
    toast.success('Response copied to clipboard!');
  };

  const handleEdit = () => {
    if (message.sender === 'user') {
      onEdit(message);
    }
  };

  return (
    <div className="message-actions-container">
      <div className="message-actions">
        <button
          className="action-btn copy-btn"
          onClick={handleCopy}
          title="Copy message"
        >
          {copied ? (
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          )}
        </button>

        {/* Edit button only for user messages */}
        {message.sender === 'user' && (
          <button
            className="action-btn edit-btn"
            onClick={handleEdit}
            title="Edit message"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
            </svg>
          </button>
        )}

        {message.sender === 'ai' && (
          <button
            className="action-btn regenerate-btn"
            onClick={() => onRegenerate(message.id)}
            title="Regenerate response"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default MessageActions;
