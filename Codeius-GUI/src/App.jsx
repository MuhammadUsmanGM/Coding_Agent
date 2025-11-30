import React, { useState, useRef, useEffect } from 'react';
import './App.css'
import Navbar from './components/Navbar/Navbar'
import InputField from './components/InputField/InputField'
import Sidebar from './components/Sidebar/Sidebar'
import ChatBubble from './components/ChatBubble/ChatBubble'

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your Codeius AI assistant. How can I help you today?",
      sender: 'ai',
      timestamp: new Date()
    }
  ]);

  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  // Scroll to bottom when messages change, but only if user hasn't scrolled up
  const shouldAutoScroll = useRef(true);

  useEffect(() => {
    const container = chatContainerRef.current;
    if (container) {
      // Check if user is near the bottom (within 100px of the bottom)
      const isNearBottom = container.scrollHeight - container.clientHeight - container.scrollTop < 100;

      // Update ref to track if we should auto-scroll
      shouldAutoScroll.current = isNearBottom;

      if (shouldAutoScroll.current) {
        // Scroll to bottom smoothly
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }
    }
  }, [messages]);

  // Add scroll listener to detect when user scrolls up
  useEffect(() => {
    const container = chatContainerRef.current;

    const handleScroll = () => {
      if (container) {
        // Check if user has scrolled up significantly (more than 100px from bottom)
        const isNearBottom = container.scrollHeight - container.clientHeight - container.scrollTop < 100;
        shouldAutoScroll.current = isNearBottom;
      }
    };

    if (container) {
      container.addEventListener('scroll', handleScroll);
    }

    return () => {
      if (container) {
        container.removeEventListener('scroll', handleScroll);
      }
    };
  }, []);

  return (
    <div className="App">
      <Navbar />
      <Sidebar />
      {/* Chat bubbles appear on the background */}
      <div className="chat-bubbles-container" ref={chatContainerRef}>
        {messages.map((message) => (
          <ChatBubble
            key={message.id}
            text={message.text}
            sender={message.sender}
            timestamp={message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>
      {/* The background image remains visible as the background of the App div */}
      <InputField setMessages={setMessages} messages={messages} />
    </div>
  )
}

export default App
