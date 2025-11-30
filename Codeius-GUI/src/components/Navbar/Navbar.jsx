import React from 'react';
import Settings from '../Settings/Settings';
import './Navbar.css';

const Navbar = () => {
  const handleModelChange = (modelId) => {
    console.log(`Model changed to: ${modelId}`);
    // Here you would typically update the selected model in your app state
  };

  return (
    <nav className="navbar">
      <div className="nav-content">
        <div className="nav-spacer"></div>
        <div className="nav-logo">
          <img src="/favicon.png" alt="Codeius AI Logo" className="logo-icon" />
          <span className="logo-text">Codeius AI</span>
        </div>
        <div className="nav-settings">
          <Settings onModelChange={handleModelChange} currentModel="groq-llama3" />
        </div>
      </div>
    </nav>
  );
};

export default Navbar;