import React, { useRef, useEffect, useState } from 'react';
import { sendMessage, getCwd, executeShellCommand, getModels, switchModel, clearHistory } from '../../services/api';
import CommandAutocomplete from '../CommandAutocomplete/CommandAutocomplete';
import { COMMANDS } from '../../utils/commands';
import './InputField.css';

const InputField = ({ setMessages, messages }) => {
  const [inputValue, setInputValue] = useState('');
  const [isShellMode, setIsShellMode] = useState(false);
  const [cwd, setCwd] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [charCount, setCharCount] = useState(0);
  const textareaRef = useRef(null);

  const handleInput = (e) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const value = e.target.value;
    setInputValue(value);
    setCharCount(value.length);

    // Show autocomplete if typing a command
    if (value.startsWith('/') && value.length > 0) {
      setShowAutocomplete(true);
    } else {
      setShowAutocomplete(false);
    }

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

  const handleSendMessage = async () => {
    if (inputValue.trim() === '') return;
    if (isSending) return;

    setIsSending(true);
    const currentInput = inputValue; // Capture input
    setInputValue(''); // Clear immediately

    // Handle Slash Commands
    if (currentInput.startsWith('/')) {
      const parts = currentInput.split(' ');
      const command = parts[0].toLowerCase();

      if (command === '/toggle') {
        setIsShellMode(prev => !prev);
        const systemMessage = {
          id: Date.now(),
          text: `Switched to ${!isShellMode ? 'Shell' : 'Interaction'} Mode`,
          sender: 'system',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, systemMessage]);
        setIsSending(false);
        return;
      }
      
      if (command === '/clear') {
        try {
          await clearHistory();
          setMessages([]); // Clear local messages
          const systemMessage = {
            id: Date.now(),
            text: 'Conversation history cleared.',
            sender: 'system',
            timestamp: new Date()
          };
          setMessages([systemMessage]);
        } catch (error) {
          const errorMessage = {
            id: Date.now(),
            text: `Failed to clear history: ${error.message}`,
            sender: 'system',
            timestamp: new Date(),
            isError: true
          };
          setMessages(prev => [...prev, errorMessage]);
        }
        setIsSending(false);
        return;
      }

      if (command === '/help') {
        const helpText = `Available Commands:
/toggle - Switch between Chat and Shell mode
/clear - Clear conversation history
/models - List available AI models
/switch [key] - Switch to a specific model
/help - Show this help message`;
        
        const systemMessage = {
          id: Date.now(),
          text: helpText,
          sender: 'system',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, systemMessage]);
        setIsSending(false);
        return;
      }

      if (command === '/models') {
        try {
          const models = await getModels();
          let modelsText = "Available Models:\n";
          Object.entries(models).forEach(([key, info]) => {
            modelsText += `- ${info.name} (${key})\n`;
          });
          
          const systemMessage = {
            id: Date.now(),
            text: modelsText,
            sender: 'system',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, systemMessage]);
        } catch (error) {
           const errorMessage = {
            id: Date.now(),
            text: `Failed to fetch models: ${error.message}`,
            sender: 'system',
            timestamp: new Date(),
            isError: true
          };
          setMessages(prev => [...prev, errorMessage]);
        }
        setIsSending(false);
        return;
      }

      if (command === '/switch') {
        const modelKey = parts[1];
        if (!modelKey) {
           const errorMessage = {
            id: Date.now(),
            text: 'Please specify a model key. Usage: /switch [key]',
            sender: 'system',
            timestamp: new Date(),
            isError: true
          };
          setMessages(prev => [...prev, errorMessage]);
          setIsSending(false);
          return;
        }

        try {
          const result = await switchModel(modelKey);
          const systemMessage = {
            id: Date.now(),
            text: result,
            sender: 'system',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, systemMessage]);
        } catch (error) {
           const errorMessage = {
            id: Date.now(),
            text: `Failed to switch model: ${error.message}`,
            sender: 'system',
            timestamp: new Date(),
            isError: true
          };
          setMessages(prev => [...prev, errorMessage]);
        }
        setIsSending(false);
        return;
      }
    }

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text: currentInput,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Shell Mode Execution
    if (isShellMode && !currentInput.startsWith('/')) {
      const loadingMessage = {
        id: messages.length + 2,
        text: "Executing...",
        sender: 'ai',
        timestamp: new Date(),
        isLoading: true
      };
      setMessages(prev => [...prev, loadingMessage]);

      try {
        const result = await executeShellCommand(currentInput);
        let outputText = result.output || '';
        if (result.error) {
          outputText = `Error: ${result.error}\n${outputText}`;
        }
        
        setMessages(prev => prev.map(msg => 
          msg.id === loadingMessage.id 
            ? { ...msg, text: outputText || "Command executed (no output)", isLoading: false } 
            : msg
        ));
      } catch (error) {
        setMessages(prev => prev.map(msg => 
          msg.id === loadingMessage.id 
            ? { ...msg, text: `Execution failed: ${error.message}`, isLoading: false, isError: true } 
            : msg
        ));
      }
      setIsSending(false);
      return;
    }

    // Normal AI Interaction
    const aiMessageId = messages.length + 2;
    const loadingMessage = {
      id: aiMessageId,
      text: "Thinking...",
      sender: 'ai',
      timestamp: new Date(),
      isLoading: true
    };
    
    setMessages(prev => [...prev, loadingMessage]);

    try {
      const response = await sendMessage(currentInput);
      
      setMessages(prev => prev.map(msg => 
        msg.id === aiMessageId 
          ? { ...msg, text: response, isLoading: false } 
          : msg
      ));
    } catch (error) {
      setMessages(prev => prev.map(msg => 
        msg.id === aiMessageId 
          ? { ...msg, text: "Sorry, I encountered an error connecting to the server.", isLoading: false, isError: true } 
          : msg
      ));
    } finally {
      setIsSending(false);
    }
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
    
    // Fetch CWD
    getCwd().then(setCwd);
  }, []);

  const handleAutocompleteSelect = (command) => {
    setInputValue(command + ' ');
    setShowAutocomplete(false);
    textareaRef.current?.focus();
  };

  return (
    <div className="input-container">
      {showAutocomplete && (
        <CommandAutocomplete
          commands={COMMANDS}
          query={inputValue}
          onSelect={handleAutocompleteSelect}
          onClose={() => setShowAutocomplete(false)}
        />
      )}
      
      <div className="input-wrapper">
        <textarea
          ref={textareaRef}
          className={`input-field ${isShellMode ? 'shell-mode' : ''}`}
          placeholder={isShellMode ? `Shell Mode (${cwd}) > Type command...` : "Ask Codeius AI anything about your code..."}
          onInput={handleInput}
          value={inputValue}
          onKeyDown={handleKeyDown}
          rows={1}
          disabled={isSending}
        />
        <button
          className="send-button"
          onClick={handleSendMessage}
          disabled={isSending || inputValue.trim() === ''}
          title="Send message (Enter)"
        >
          {isSending ? '⏳' : '📤'}
        </button>
      </div>
      
      <div className="input-footer">
        {cwd && (
          <div className="cwd-display">
            📁 {cwd}
          </div>
        )}
        {charCount > 0 && (
          <div className="char-counter">
            {charCount} characters
          </div>
        )}
      </div>
    </div>
  );
};

export default InputField;