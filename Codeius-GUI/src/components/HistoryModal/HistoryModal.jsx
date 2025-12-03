import React, { useState, useEffect } from 'react';
import { getSessions, deleteSession, createNewSession, setCurrentSessionId, getCurrentSessionId } from '../../utils/localStorage';
import { useToast } from '../Toast/ToastContainer';
import ConfirmationDialog from '../ConfirmationDialog/ConfirmationDialog';
import './HistoryModal.css';

const HistoryModal = ({ isOpen, onClose }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setSessionId] = useState(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [sessionToDelete, setSessionToDelete] = useState(null);
  const toast = useToast();

  // Load sessions when modal opens
  useEffect(() => {
    if (isOpen) {
      setSessions(getSessions());
      setSessionId(getCurrentSessionId());
    }
  }, [isOpen]);

  const handleSessionClick = (sessionId) => {
    setCurrentSessionId(sessionId);
    window.location.reload(); // Reload to load the selected session
  };

  const handleDeleteSessionConfirm = () => {
    if (sessionToDelete) {
      deleteSession(sessionToDelete);
      setSessions(getSessions()); // Refresh list
      toast.success('Chat deleted successfully!');

      // If deleted current session, reload to create a new one
      if (sessionToDelete === currentSessionId) {
        window.location.reload();
      }

      setShowConfirmDialog(false);
      setSessionToDelete(null);
    }
  };

  const handleDeleteSession = (e, sessionId) => {
    e.stopPropagation();
    setSessionToDelete(sessionId);
    setShowConfirmDialog(true);
  };

  const handleNewChat = () => {
    createNewSession();
    window.location.reload();
  };

  if (!isOpen) return null;

  return (
    <div className="history-modal-overlay open" onClick={onClose}>
      <div className="history-modal" onClick={(e) => e.stopPropagation()}>
        <div className="history-modal-header">
          <h2>Chat History</h2>
          <button className="new-chat-btn-header" onClick={handleNewChat}>
            + New Chat
          </button>
        </div>

        <div className="history-modal-content">
          {sessions.length > 0 ? (
            <div className="history-list">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`history-item session-item ${session.id === currentSessionId ? 'active' : ''}`}
                  onClick={() => handleSessionClick(session.id)}
                >
                  <div className="session-info">
                    <div className="session-title">{session.title || 'New Chat'}</div>
                    <div className="session-preview">{session.preview || 'No messages yet'}</div>
                    <div className="session-meta">
                      <span className="session-date">{new Date(session.lastModified).toLocaleDateString()}</span>
                      <span className="session-count">{session.messageCount} msgs</span>
                    </div>
                  </div>
                  <button
                    className="delete-session-btn"
                    onClick={(e) => handleDeleteSession(e, session.id)}
                    title="Delete chat"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="history-empty">
              <p>No chat history yet</p>
            </div>
          )}
        </div>

        <div className="history-modal-footer">
          <button className="close-history-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
      {/* Confirmation dialog for delete actions */}
      <ConfirmationDialog
        isOpen={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
        onConfirm={handleDeleteSessionConfirm}
        title="Delete Chat"
        message="Are you sure you want to delete this chat? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />
    </div>
  );
};

export default HistoryModal;