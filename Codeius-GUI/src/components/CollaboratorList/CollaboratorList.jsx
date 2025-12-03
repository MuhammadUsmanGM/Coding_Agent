import React, { useState, useEffect } from 'react';
import socketService from '../../services/socket';
import { shareSession } from '../../services/api';
import { useToast } from '../Toast/ToastContainer';
import './CollaboratorList.css';

const CollaboratorList = ({ sessionId }) => {
  const [users, setUsers] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const dropdownRef = React.useRef(null);
  const toast = useToast();

  useEffect(() => {
    // Initial self
    setUsers([{ id: 'me', name: 'You' }]);

    const handleUserJoined = (data) => {
      setUsers(prev => [...prev, { id: Date.now(), name: data.user || 'Anonymous' }]);
    };

    const handleUserLeft = (data) => {
      setUsers(prev => prev.slice(0, -1)); // Simple removal for demo
    };

    socketService.on('user_joined', handleUserJoined);
    socketService.on('user_left', handleUserLeft);

    // Click outside handler
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);

    return () => {
      socketService.off('user_joined', handleUserJoined);
      socketService.off('user_left', handleUserLeft);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleInvite = async () => {
    if (isSharing) return;
    setIsSharing(true);
    try {
      // Use current session ID from props or fallback
      const currentSessionId = sessionId === 'current-session' 
        ? localStorage.getItem('current_session_id') 
        : sessionId;
        
      if (!currentSessionId) {
        toast.error("No active session to share");
        return;
      }

      const url = await shareSession(currentSessionId);
      await navigator.clipboard.writeText(url);
      toast.success("Share link copied to clipboard!");
      setIsOpen(false);
    } catch (error) {
      toast.error("Failed to generate share link");
    } finally {
      setIsSharing(false);
    }
  };

  return (
    <div className="collaborator-container" ref={dropdownRef}>
      <div 
        className="collaborator-list" 
        title="Active Collaborators"
        onClick={() => setIsOpen(!isOpen)}
      >
        {users.slice(0, 3).map((user, index) => (
          <div key={index} className="collaborator-avatar" style={{backgroundColor: getColor(index)}}>
            {user.name[0]}
          </div>
        ))}
        {users.length > 3 && (
          <div className="collaborator-more">+{users.length - 3}</div>
        )}
        {users.length > 1 && (
          <span className="collaborator-count">{users.length} online</span>
        )}
      </div>

      {isOpen && (
        <div className="collaborator-dropdown">
          <div className="dropdown-header">Active Users ({users.length})</div>
          <div className="dropdown-list">
            {users.map((user, index) => (
              <div key={index} className="dropdown-item">
                <div className="dropdown-avatar" style={{backgroundColor: getColor(index)}}>
                  {user.name[0]}
                </div>
                <span className="dropdown-name">{user.name}</span>
                {user.id === 'me' && <span className="dropdown-badge">You</span>}
              </div>
            ))}
          </div>
          <div className="dropdown-footer">
            <button 
              className="invite-btn" 
              onClick={handleInvite}
              disabled={isSharing}
            >
              {isSharing ? 'Generating...' : 'Invite Collaborator'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

const getColor = (index) => {
  const colors = ['#007acc', '#4ec9b0', '#ce9178', '#dcdcaa', '#b5cea8'];
  return colors[index % colors.length];
};

export default CollaboratorList;
