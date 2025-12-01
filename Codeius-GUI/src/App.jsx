import React, { useState, useRef, useEffect, useCallback, lazy, Suspense } from 'react';
import Navbar from './components/Navbar/Navbar'
import InputField from './components/InputField/InputField'
import ChatBubble from './components/ChatBubble/ChatBubble'
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import StopButton from './components/StopButton/StopButton';
import socketService from './services/socket';
import { saveSessionMessages, getSessionMessages, getCurrentSessionId, loadMessages } from './utils/localStorage'
import { useToast, ToastProvider } from './components/Toast/ToastContainer';
import ConfirmationDialog from './components/ConfirmationDialog/ConfirmationDialog';
import LoadingSpinner from './components/LoadingSpinner/LoadingSpinner';
import './App.css'

import SearchModal from './components/SearchModal/SearchModal';

function AppContent() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [currentModel, setCurrentModel] = useState(''); // Track current model
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [messageToDelete, setMessageToDelete] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState(null);
  const [showSearch, setShowSearch] = useState(false);
  const sessionId = useRef(`session_${Date.now()}`);

  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);
  const inputFieldRef = useRef(null);
  const toast = useToast();

  // Focus input field when component mounts and when there are no messages (new chat)
  useEffect(() => {
    if (messages.length === 0) {
      // Add a small delay to ensure the input field is rendered
      setTimeout(() => {
        if (inputFieldRef.current) {
          inputFieldRef.current.focus();
        }
      }, 100);
    }
  }, [messages.length]); // Only run when messages.length changes

  // Load messages on mount
  useEffect(() => {
    const currentSessionId = getCurrentSessionId();
    const savedMessages = getSessionMessages(currentSessionId);
    if (savedMessages && savedMessages.length > 0) {
      setMessages(savedMessages);
    } else {
      // If no messages for the current session, initialize with empty array
      setMessages([]);
    }
  }, []);

  // Function to open history modal
  const openHistoryModal = () => {
    setIsHistoryModalOpen(true);
  };

  // Function to close history modal
  const closeHistoryModal = () => {
    setIsHistoryModalOpen(false);
  };

  // Auto-save messages to localStorage
  useEffect(() => {
    const currentSessionId = getCurrentSessionId();
    saveSessionMessages(currentSessionId, messages);
  }, [messages]);

  // Message action handlers
  const handleCopyMessage = (text) => {
    navigator.clipboard.writeText(text);
  };

  const handleRegenerateMessage = async (messageId) => {
    // Find the message to regenerate
    const messageIndex = messages.findIndex(msg => msg.id === messageId);
    if (messageIndex === -1) return;

    // Find the user's prompt (previous message)
    const userMessage = messages[messageIndex - 1];
    if (!userMessage || userMessage.sender !== 'user') return;

    // Remove the AI message and regenerate
    const updatedMessages = messages.filter(msg => msg.id !== messageId);
    setMessages(updatedMessages);

    // Trigger regeneration by sending the same prompt
    // This will be handled by InputField's sendMessage function
    // For now, we'll just show a system message
    const systemMsg = {
      id: Date.now(),
      text: 'Regenerating response...',
      sender: 'system',
      timestamp: new Date()
    };
    setMessages([...updatedMessages, systemMsg]);
  };

  const handleEditMessage = (message) => {
    // Set the message text in the input field for editing
    setInputValue(message.text);
    // Focus the input field to make it clear that it's in edit mode
    setTimeout(() => {
      const inputField = document.querySelector('.input-field');
      if (inputField) {
        inputField.focus();
        // Move cursor to the end of the text
        inputField.selectionStart = inputField.value.length;
        inputField.selectionEnd = inputField.value.length;
      }
    }, 100);
  };

  const handleModelChange = (modelId) => {
    setCurrentModel(modelId);
    toast.success(`Model changed to: ${modelId}`);
  };

  const handleDeleteMessageConfirm = () => {
    if (messageToDelete) {
      setMessages(messages.filter(msg => msg.id !== messageToDelete));
      toast.success('Message deleted successfully!');
      setShowConfirmDialog(false);
      setMessageToDelete(null);
    }
  };

  const handleDeleteMessage = (messageId) => {
    setMessageToDelete(messageId);
    setShowConfirmDialog(true);
  };

  // Always auto-scroll to latest message
  const shouldAutoScroll = useRef(true);

  useEffect(() => {
    const container = chatContainerRef.current;
    if (container && messages.length > 0) {
      const isNearBottom = container.scrollHeight - container.clientHeight - container.scrollTop < 100;

      if (isNearBottom || shouldAutoScroll.current) {
        setTimeout(() => {
          messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      }
    }
  }, [messages]);

  // Track user scroll position to pause auto-scroll
  useEffect(() => {
    const container = chatContainerRef.current;

    const handleScroll = () => {
      if (container) {
        const isNearBottom = container.scrollHeight - container.clientHeight - container.scrollTop < 100;
        shouldAutoScroll.current = isNearBottom;
      }
    };

    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => {
        container.removeEventListener('scroll', handleScroll);
      };
    }
  }, []);

  // WebSocket streaming setup
  useEffect(() => {
    socketService.connect();

    socketService.on('stream_start', (data) => {
      if (data.session_id === sessionId.current) {
        setIsStreaming(true);
        setStreamingMessage({
          id: Date.now(),
          text: '',
          sender: 'ai',
          timestamp: new Date(),
          isStreaming: true
        });
      }
    });

    socketService.on('stream_token', (data) => {
      if (data.session_id === sessionId.current) {
        setStreamingMessage(prev => prev ? {
          ...prev,
          text: prev.text + data.token
        } : null);
      }
    });

    socketService.on('stream_end', (data) => {
      if (data.session_id === sessionId.current) {
        setIsStreaming(false);
        if (streamingMessage) {
          setMessages(prev => [...prev, {
            ...streamingMessage,
            isStreaming: false
          }]);
          setStreamingMessage(null);
        }
      }
    });

    socketService.on('stream_error', (data) => {
      if (data.session_id === sessionId.current) {
        setIsStreaming(false);
        toast.error(`Streaming error: ${data.error}`);
        setStreamingMessage(null);
      }
    });

    return () => {
      socketService.disconnect();
    };
  }, [toast]);

  const handleStopStreaming = () => {
    socketService.emit('cancel_stream', { session_id: sessionId.current });
    setIsStreaming(false);
    if (streamingMessage && streamingMessage.text) {
      setMessages(prev => [...prev, {
        ...streamingMessage,
        isStreaming: false
      }]);
    }
    setStreamingMessage(null);
  };

  // Add keyboard navigation functionality
  useEffect(() => {
    const container = chatContainerRef.current;

    const handleKeyDown = (e) => {
      // Global shortcuts
      if (e.ctrlKey && e.key === '/') {
        e.preventDefault();
        setShowShortcuts(prev => !prev);
        return;
      }

      if (e.ctrlKey && e.key === 'l') {
        e.preventDefault();
        // Clear messages
        setMessages([{
          id: 1,
          text: "Conversation cleared. How can I help you?",
          sender: 'system',
          timestamp: new Date()
        }]);
        return;
      }

      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        // Focus input field
        document.querySelector('.input-field')?.focus();
        return;
      }

      // Only respond to navigation keys if the input field is not focused
      if (!document.activeElement.classList.contains('input-field')) {
        if (e.key === 'ArrowUp' && container) {
          e.preventDefault();
          // Scroll up by roughly 100px or to the top if near the top
          container.scrollTop = Math.max(0, container.scrollTop - 100);
        } else if (e.key === 'ArrowDown' && container) {
          e.preventDefault();
          // Scroll down by roughly 100px or to the bottom if near the bottom
          const maxScroll = container.scrollHeight - container.clientHeight;
          container.scrollTop = Math.min(maxScroll, container.scrollTop + 100);
        } else if (e.key === 'Home' && container) {
          e.preventDefault();
          // Scroll to top
          container.scrollTop = 0;
        } else if (e.key === 'End' && container) {
          e.preventDefault();
          // Scroll to bottom
          container.scrollTop = container.scrollHeight;
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  return (
    <div className="App">
      <Navbar
        onOpenHistory={openHistoryModal}
        onModelChange={handleModelChange}
        currentModel={currentModel}
      />
      <Sidebar />
      <div className="git-controls-container">
        <GitControls />
      </div>
      {/* Chat bubbles appear on the background */}
      <ErrorBoundary>
        <div className="chat-container" ref={chatContainerRef}>
          {/* Settings Modal */}
          <Suspense fallback={<LoadingSpinner size="medium" />}>
            {showSettings && (
              <Settings
                onClose={() => setShowSettings(false)}
                onModelChange={handleModelChange}
                currentModel={currentModel}
              />
            )}
          </Suspense>

          {/* History Modal */}
          <Suspense fallback={<LoadingSpinner size="medium" />}>
            {showHistory && (
              <HistoryModal
                isOpen={showHistory}
                onClose={() => setShowHistory(false)}
                onSelectConversation={loadHistoryConversation}
              />
            )}
          </Suspense>

          {/* Search Modal */}
          <SearchModal
            isOpen={showSearch}
            onClose={() => setShowSearch(false)}
            messages={messages}
            onSelectMessage={handleSearchResultSelect}
          />

          {messages.map((message) => (
            <ChatBubble
              key={message.id}
              text={message.text}
              sender={message.sender}
              timestamp={message.timestamp}
              isLoading={message.isLoading}
              message={message}
              onCopy={handleCopyMessage}
              onRegenerate={handleRegenerateMessage}
              onDelete={handleDeleteMessage}
              onEdit={handleEditMessage}
            />
          ))}
          {streamingMessage && (
            <ChatBubble
              key="streaming"
              text={streamingMessage.text}
              sender={streamingMessage.sender}
              timestamp={streamingMessage.timestamp}
              message={streamingMessage}
            />
          )}
          <div ref={messagesEndRef} />
        </div>
      </ErrorBoundary>
      <StopButton isStreaming={isStreaming} onStop={handleStopStreaming} />
      {/* The background image remains visible as the background of the App div */}
      <InputField
        ref={inputFieldRef}
        setMessages={setMessages}
        messages={messages}
        inputValue={inputValue}
        setInputValue={setInputValue}
      />
      {/* History modal */}
      <ErrorBoundary>
        <HistoryModal isOpen={isHistoryModalOpen} onClose={closeHistoryModal} />
      </ErrorBoundary>
      {/* Keyboard shortcuts overlay */}
      <KeyboardShortcuts isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
      {/* Confirmation dialog for delete actions */}
      <ConfirmationDialog
        isOpen={showConfirmDialog}
        onClose={() => setShowConfirmDialog(false)}
        onConfirm={handleDeleteMessageConfirm}
        title="Delete Message"
        message="Are you sure you want to delete this message? This action cannot be undone."
        confirmText="Delete"
        cancelText="Cancel"
        type="danger"
      />
    </div>
  )
}

function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}

export default App
