import React, { useRef, useEffect, useState } from 'react';
import './InputField.css';

const InputField = ({ setMessages, messages }) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef(null);

  const handleInput = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to auto to calculate the proper scrollHeight
    textarea.style.height = 'auto';

    // Calculate the new height based on content
    const maxHeight = 150; // Max height for 4 lines

    if (textarea.scrollHeight > maxHeight) {
      textarea.style.height = `${maxHeight}px`;
      textarea.style.overflowY = 'auto';
    } else {
      textarea.style.height = `${textarea.scrollHeight}px`;
      textarea.style.overflowY = 'hidden';
    }
  };

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Simulate AI response after a delay
    setTimeout(() => {
      const aiMessage = {
        id: messages.length + 2,
        text: "Thank you for your message! This is a simulated response from the AI assistant. In the full implementation, this would connect to the actual AI backend.",
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
    }, 1000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  useEffect(() => {
    // Set initial height on mount
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
    }
  }, []);

  return (
    <div className="input-container">
      <textarea
        ref={textareaRef}
        className="input-field"
        placeholder="Ask Codeius AI anything about your code..."
        onInput={handleInput}
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
      />
    </div>
  );
};

export default InputField;