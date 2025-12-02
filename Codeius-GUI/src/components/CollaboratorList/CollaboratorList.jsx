import React, { useState, useEffect } from 'react';
import socketService from '../../services/socket';
import './CollaboratorList.css';

const CollaboratorList = ({ sessionId }) => {
  const [users, setUsers] = useState([]);

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

    return () => {
      socketService.off('user_joined', handleUserJoined);
      socketService.off('user_left', handleUserLeft);
    };
  }, []);

  return (
    <div className="collaborator-list" title="Active Collaborators">
      {users.map((user, index) => (
        <div key={index} className="collaborator-avatar" style={{backgroundColor: getColor(index)}}>
          {user.name[0]}
        </div>
      ))}
      {users.length > 1 && (
        <span className="collaborator-count">{users.length} online</span>
      )}
    </div>
  );
};

const getColor = (index) => {
  const colors = ['#007acc', '#4ec9b0', '#ce9178', '#dcdcaa', '#b5cea8'];
  return colors[index % colors.length];
};

export default CollaboratorList;
