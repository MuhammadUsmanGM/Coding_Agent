import React from 'react';
import './StopButton.css';

const StopButton = ({ onStop, isStreaming }) => {
  if (!isStreaming) return null;

  return (
    <button 
      className="stop-generation-btn" 
      onClick={onStop}
      title="Stop generating response"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
        <rect x="6" y="6" width="12" height="12" rx="2"/>
      </svg>
      <span>Stop Generating</span>
    </button>
  );
};

export default StopButton;
