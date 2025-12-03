import React, { useRef, useEffect, useState, forwardRef } from 'react';
import socketService from '../../services/socket';
import { getCwd, executeShellCommand, getModels, switchModel, clearHistory, getFiles } from '../../services/api';
import CommandAutocomplete from '../CommandAutocomplete/CommandAutocomplete';
import { COMMANDS } from '../../utils/commands';
import FileUpload from '../FileUpload/FileUpload';
import './InputField.css';

const InputField = forwardRef(({ setMessages, messages, inputValue, setInputValue }, ref) => {
  const [isSending, setIsSending] = useState(false);
  const [cwd, setCwd] = useState('');
  const [showAutocomplete, setShowAutocomplete] = useState(false);
  const [showFileAutocomplete, setShowFileAutocomplete] = useState(false);
  const [fileSuggestions, setFileSuggestions] = useState([]);
  const [charCount, setCharCount] = useState(inputValue?.length || 0);
  const [isShellMode, setIsShellMode] = useState(false);
  const textareaRef = useRef(null);

  // Use the forwarded ref to access the textarea
  useEffect(() => {
    if (ref) {
      if (typeof ref === 'function') {
        ref(textareaRef.current);
      } else {
        ref.current = textareaRef.current;
      }
    }
  }, [ref]);

  // Update local state when parent state changes
  useEffect(() => {
    setCharCount(inputValue?.length || 0);
  }, [inputValue]);

  const handleInput = async (e) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const value = e.target.value;
    setInputValue(value);
    setCharCount(value.length);

    // Show autocomplete if typing a command
    if (value.startsWith('/') && value.length > 0) {
      setShowAutocomplete(true);
      setShowFileAutocomplete(false);
    } else if (value.includes('@')) {
       // File Autocomplete Logic
       const lastWord = value.split(/\s+/).pop();
       if (lastWord.startsWith('@')) {
         const pathQuery = lastWord.slice(1);
         setShowFileAutocomplete(true);
         setShowAutocomplete(false);
         
         try {
           // Determine directory to search
           // If pathQuery ends with /, search that directory
           // If not, search the parent directory
           let searchPath = '.';
           if (pathQuery.includes('/')) {
             const lastSlashIndex = pathQuery.lastIndexOf('/');
             searchPath = pathQuery.substring(0, lastSlashIndex) || '.';
           }
           
           const files = await getFiles(searchPath);
           
           // Transform files to autocomplete format
           const suggestions = files.map(f => ({
             cmd: f.path, // The full relative path
             desc: f.type === 'directory' ? 'Folder' : 'File'
           }));
           
           setFileSuggestions(suggestions);
         } catch (err) {
           console.error("Failed to fetch files for autocomplete", err);
         }
       } else {
         setShowFileAutocomplete(false);
       }
    } else {
      setShowAutocomplete(false);
      setShowFileAutocomplete(false);
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
    setInputValue(''); // Clear immediately using parent state
    setShowAutocomplete(false);
    setShowFileAutocomplete(false);

    // Handle Slash Commands
    if (currentInput.startsWith('/')) {
      const parts = currentInput.split(' ');
      const command = parts[0].toLowerCase();

      // 1. Handle implemented local commands
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

      // 2. Check if it's a known command but NOT implemented in GUI
      const isKnownCommand = COMMANDS.some(c => c.cmd.startsWith(command));
      if (isKnownCommand) {
         const warningMessage = {
            id: Date.now(),
            text: `Command '${command}' is not yet supported in the GUI.`,
            sender: 'system',
            timestamp: new Date(),
            isError: true
          };
          setMessages(prev => [...prev, warningMessage]);
          setIsSending(false);
          return;
      }

      // 3. Unknown command - Block it
       const warningMessage = {
          id: Date.now(),
          text: `Unknown command: '${command}'. Type /help for available commands.`,
          sender: 'system',
          timestamp: new Date(),
          isError: true
        };
        setMessages(prev => [...prev, warningMessage]);
        setIsSending(false);
        return;
    }

    // Add user message
    const userMessage = {
      id: Date.now(),
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

    // Use WebSocket streaming for response
    try {
      const sessionId = localStorage.getItem('current_session_id') || `session_${Date.now()}`;
      localStorage.setItem('current_session_id', sessionId);
      
      socketService.emit('start_stream', {
        prompt: currentInput,
        session_id: sessionId
      });
    } catch (error) {
      console.error('Error starting stream:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: 'Sorry, there was an error processing your request.',
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    }

    setIsSending(false);
  };

  const handleKeyDown = (e) => {
    // If autocomplete is open, let it handle navigation/selection via its own listeners
    // We just need to prevent the Enter key from submitting the message
    if ((showAutocomplete || showFileAutocomplete) && e.key === 'Enter') {
      e.preventDefault();
      return;
    }

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handlePaste = (e) => {
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

  const handleFileSelect = (path) => {
    // Replace the last word (which is the partial path) with the selected path
    const words = inputValue.split(/\s+/);
    words.pop(); // Remove partial
    const newValue = words.join(' ') + (words.length > 0 ? ' ' : '') + '@' + path + ' ';
    setInputValue(newValue);
    setShowFileAutocomplete(false);
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
          title="Commands"
          triggerChar="/"
        />
      )}
      
      {showFileAutocomplete && (
        <CommandAutocomplete
          commands={fileSuggestions}
          query={inputValue.split(/\s+/).pop()} // Pass only the last word as query
          onSelect={handleFileSelect}
          onClose={() => setShowFileAutocomplete(false)}
          title="Files"
          triggerChar="@"
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
          {isSending ? (
            <div className="loading-spinner"></div>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          )}
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
});

export default InputField;