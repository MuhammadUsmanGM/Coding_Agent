import React, { useState } from 'react';
import Settings from '../Settings/Settings';
import HistoryIcon from '../HistoryIcon/HistoryIcon';
import ContextPanel from '../ContextPanel/ContextPanel';
import ExportMenu from '../ExportMenu/ExportMenu';
import CollaboratorList from '../CollaboratorList/CollaboratorList';
import './Navbar.css';

const Navbar = ({ onOpenHistory, onModelChange, currentModel, user, messages }) => {
  const [showContext, setShowContext] = useState(false);

  return (
    <>
      <nav className="navbar">
        <div className="nav-content">
          <div className="nav-spacer"></div>
          <div className="nav-logo">
            <img src="/favicon.png" alt="Codeius AI Logo" className="logo-icon" />
            <span className="logo-text">Codeius AI</span>
          </div>
          <div className="nav-controls">
            <CollaboratorList sessionId="current-session" />
            {messages && messages.length > 0 && (
              <ExportMenu messages={messages} elementId="chat-container" />
            )}
            <button className="context-btn" onClick={() => setShowContext(true)} title="View Project Context">
              🧠 Context
            </button>
            <HistoryIcon onOpenHistory={onOpenHistory} />
            <Settings onModelChange={onModelChange} currentModel={currentModel} />
          </div>
        </div>
      </nav>
      <ContextPanel isOpen={showContext} onClose={() => setShowContext(false)} />
    </>
  );
};

export default Navbar;