import React from 'react';
import ChatBubble from '../ChatBubble/ChatBubble';
import './ChatContainer.css';

const ChatContainer = ({ messages }) => {
  return (
    <div className="chat-container">
      {messages.map((message) => (
        <ChatBubble
          key={message.id}
          text={message.text}
          sender={message.sender}
          timestamp={message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        />
      ))}
    </div>
  );
};

export default ChatContainer;