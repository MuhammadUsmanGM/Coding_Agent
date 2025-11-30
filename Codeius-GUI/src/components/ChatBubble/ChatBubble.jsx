import React from 'react';
import './ChatBubble.css';

const ChatBubble = ({ text, sender, timestamp }) => {
  return (
    <div className={`chat-bubble ${sender}-bubble`}>
      <div className="bubble-content">
        <div className="bubble-text">{text}</div>
        <div className="bubble-timestamp">{timestamp}</div>
      </div>
    </div>
  );
};

export default ChatBubble;