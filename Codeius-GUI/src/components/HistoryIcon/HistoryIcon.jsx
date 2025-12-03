import React from 'react';
import './HistoryIcon.css';

const HistoryIcon = ({ onOpenHistory }) => {
  return (
    <button
      className="history-icon-btn"
      onClick={onOpenHistory}
      aria-label="Open chat history"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="history-icon-svg"
      >
        <circle cx="12" cy="12" r="10" stroke="#87ceeb" />
        <polyline points="12 6 12 12 16 14" stroke="#87ceeb" />
      </svg>
    </button>
  );
};

export default HistoryIcon;