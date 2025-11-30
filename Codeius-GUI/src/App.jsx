import React, { useState } from 'react';
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

  return (
    <div className="App">
      <Navbar />
      <Sidebar />
      {/* Chat bubbles appear on the background */}
      <div className="chat-bubbles-container">
        {messages.map((message) => (
          <ChatBubble
            key={message.id}
            text={message.text}
            sender={message.sender}
            timestamp={message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          />
        ))}
      </div>
      {/* The background image remains visible as the background of the App div */}
      <InputField setMessages={setMessages} messages={messages} />
    </div>
  )
}

export default App
