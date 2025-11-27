import { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { id: 1, content: 'Hello! I\'m your Codeius AI assistant. How can I help you with your coding today?', sender: 'ai', timestamp: new Date() }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [availableModels, setAvailableModels] = useState({});
  const [currentModel, setCurrentModel] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState('default');
  const [showSettings, setShowSettings] = useState(false);
  const [showTour, setShowTour] = useState(false);
  const [userPreferences, setUserPreferences] = useState({
    fontSize: 'medium',
    codeHighlighting: 'auto',
    notifications: true,
    autoScroll: true,
    sidebarPosition: 'left'
  });
  const [showCodeEditor, setShowCodeEditor] = useState(false);
  const [codeEditorContent, setCodeEditorContent] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef(null);

  // Load available models and user preferences on component mount
  useEffect(() => {
    fetchModels();
    loadUserPreferences();

    // Show tour for first-time users
    if (!localStorage.getItem('hasSeenTour')) {
      setShowTour(true);
      localStorage.setItem('hasSeenTour', 'true');
    }
  }, []);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('codeius-theme', theme);
  }, [theme]);

  // Scroll to bottom of messages when it changes
  useEffect(() => {
    if (userPreferences.autoScroll) {
      scrollToBottom();
    }
  }, [messages, userPreferences.autoScroll]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/models`);
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`${response.status} - ${errorText}`);
      }
      const data = await response.json();
      setAvailableModels(data.models);

      // Set the first model as current if none is set
      if (Object.keys(data.models).length > 0 && !currentModel) {
        const firstModelKey = Object.keys(data.models)[0];
        setCurrentModel(firstModelKey);
      }
    } catch (error) {
      console.error('Error fetching models:', error);
      // Add a message to the chat about the error
      setMessages(prev => [...prev, {
        id: Date.now(),
        content: `⚠️ Backend server not available. Please make sure the Codeius backend is running. Error: ${error.message}`,
        sender: 'system',
        timestamp: new Date()
      }]);
    }
  };

  const loadUserPreferences = () => {
    const savedPrefs = localStorage.getItem('codeius-prefs');
    if (savedPrefs) {
      setUserPreferences(JSON.parse(savedPrefs));
    }

    const savedTheme = localStorage.getItem('codeius-theme');
    if (savedTheme) {
      setTheme(savedTheme);
    }
  };

  const saveUserPreferences = (prefs) => {
    setUserPreferences(prefs);
    localStorage.setItem('codeius-prefs', JSON.stringify(prefs));
  };

  const switchTheme = (themeName) => {
    setTheme(themeName);
    localStorage.setItem('codeius-theme', themeName);
  };

  const updatePreferences = (newPrefs) => {
    const updatedPrefs = { ...userPreferences, ...newPrefs };
    saveUserPreferences(updatedPrefs);
  };

  const openCodeEditor = (initialCode = '') => {
    setCodeEditorContent(initialCode);
    setShowCodeEditor(true);
  };

  const insertCode = (code) => {
    setInputValue(prev => prev + code);
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // Handle special commands
    if (inputValue.startsWith('/')) {
      if (inputValue === '/clear') {
        setMessages([]);
        setInputValue('');
        return;
      } else if (inputValue === '/help') {
        const helpMessage = {
          id: Date.now(),
          content: [
            'Available commands:',
            '/help - Show available commands',
            '/models - List AI models',
            '/switch [key] - Switch AI model',
            '/context - Show project context',
            '/clear - Clear chat',
            '/test - Run a test command',
            '/themes - Show available themes',
            '/settings - Open settings panel',
            '/history - Show conversation history',
            '/editor - Open code editor',
          ].join('\n'),
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, helpMessage]);
        setInputValue('');
        return;
      } else if (inputValue === '/themes') {
        const themesMessage = {
          id: Date.now(),
          content: 'Available themes: default, light, blue, green. Use /theme [name] to switch.',
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, themesMessage]);
        return;
      } else if (inputValue.startsWith('/theme ')) {
        const themeName = inputValue.split(' ')[1];
        const availableThemes = ['default', 'light', 'blue', 'green'];
        if (availableThemes.includes(themeName)) {
          switchTheme(themeName);
          const themeMessage = {
            id: Date.now(),
            content: `Theme switched to ${themeName}`,
            sender: 'system',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, themeMessage]);
        } else {
          const errorMessage = {
            id: Date.now(),
            content: `Invalid theme: ${themeName}. Available themes: ${availableThemes.join(', ')}`,
            sender: 'system',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, errorMessage]);
        }
        setInputValue('');
        return;
      } else if (inputValue === '/settings') {
        setShowSettings(true);
        setInputValue('');
        return;
      } else if (inputValue === '/history') {
        setShowHistory(true);
        setInputValue('');
        return;
      } else if (inputValue === '/editor') {
        openCodeEditor('');
        setInputValue('');
        return;
      } else if (inputValue.startsWith('/switch ')) {
        // Handle model switching
        const modelKey = inputValue.split(' ')[1];
        if (modelKey && availableModels[modelKey]) {
          try {
            const response = await fetch(`${API_BASE_URL}/switch_model`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ model_key: modelKey }),
            });

            if (!response.ok) {
              throw new Error(`Failed to switch model: ${response.statusText}`);
            }

            const data = await response.json();
            const systemMessage = {
              id: Date.now() + 1,
              content: data.result,
              sender: 'system',
              timestamp: new Date()
            };
            setMessages(prev => [...prev, systemMessage]);
            setCurrentModel(modelKey);
          } catch (error) {
            const errorMessage = {
              id: Date.now() + 1,
              content: `Error switching model: ${error.message}`,
              sender: 'system',
              timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
          }
        } else {
          const errorMessage = {
            id: Date.now() + 1,
            content: `Invalid model key: ${modelKey}. Use /models to see available models.`,
            sender: 'system',
            timestamp: new Date()
          };
          setMessages(prev => [...prev, errorMessage]);
        }
        setInputValue('');
        return;
      } else if (inputValue === '/models') {
        const modelsList = Object.entries(availableModels).map(([key, model]) =>
          `${key}: ${model.name} (${model.provider})`
        ).join('\n');

        const modelMessage = {
          id: Date.now(),
          content: modelsList || 'No models available',
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, modelMessage]);
        setInputValue('');
        return;
      }
      // If it's not one of the handled commands, treat as regular message
    }

    const userMessage = {
      id: Date.now(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: inputValue }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`${response.status} - ${errorText}`);
      }

      const data = await response.json();
      const aiMessage = {
        id: Date.now() + 1,
        content: data.response,
        sender: 'ai',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        content: `Sorry, I encountered an error: ${error.message}`,
        sender: 'system',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    sendMessage();
  };

  const runCommand = (cmd) => {
    setInputValue(cmd);
    setTimeout(() => {
      document.getElementById('message-form')?.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
    }, 100);
  };

  const quickActions = [
    { title: "Explain Code", prompt: "Can you explain how this code works?", icon: "🧩" },
    { title: "Fix Error", prompt: "I'm getting this error, how do I fix it?", icon: "🔧" },
    { title: "Optimize Code", prompt: "How can I optimize this code?", icon: "💨" },
    { title: "Write Unit Test", prompt: "Write a unit test for this function", icon: "🧪" },
  ];

  const tourSteps = [
    { id: 1, title: "Welcome to Codeius!", content: "This is your AI-powered coding assistant. You can ask questions about code, get debugging help, and more!" },
    { id: 2, title: "Try Quick Actions", content: "Use these buttons for common tasks like explaining code, fixing errors, or optimizing code." },
    { id: 3, title: "Use Commands", content: "Type /help to see all available commands. You can switch models, search code, and perform many tasks." },
    { id: 4, title: "Customize Your Experience", content: "Click the gear icon to access settings. You can change themes and adjust preferences." },
  ];

  // Define available commands for the sidebar
  const commands = [
    { name: '/help', description: 'Show available commands' },
    { name: '/models', description: 'List AI models' },
    { name: '/switch [key]', description: 'Switch AI model' },
    { name: '/context', description: 'Show project context' },
    { name: '/set_project [path]', description: 'Set project context' },
    { name: '/search [query]', description: 'Search codebase' },
    { name: '/security_scan', description: 'Run security scan' },
    { name: '/plugins', description: 'List plugins' },
    { name: '/analyze', description: 'Analyze project' },
    { name: '/dashboard', description: 'Show dashboard' },
    { name: '/themes', description: 'Show themes' },
    { name: '/settings', description: 'Open settings panel' },
    { name: '/history', description: 'Show conversation history' },
    { name: '/editor', description: 'Open code editor' },
    { name: '/test', description: 'Run tests' },
    { name: '/clear', description: 'Clear chat' },
  ];

  // Settings panel component
  const SettingsPanel = () => (
    <div className="settings-panel" onClick={() => setShowSettings(false)}>
      <div className="settings-content" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h3>Settings</h3>
          <button className="close-settings" onClick={() => setShowSettings(false)}>✕</button>
        </div>

        <div className="setting-item">
          <label>Theme</label>
          <select
            value={theme}
            onChange={(e) => switchTheme(e.target.value)}
          >
            <option value="default">Default</option>
            <option value="light">Light</option>
            <option value="blue">Blue</option>
            <option value="green">Green</option>
          </select>
        </div>

        <div className="setting-item">
          <label>Font Size</label>
          <select
            value={userPreferences.fontSize}
            onChange={(e) => updatePreferences({ fontSize: e.target.value })}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>

        <div className="setting-item">
          <label>Code Highlighting</label>
          <select
            value={userPreferences.codeHighlighting}
            onChange={(e) => updatePreferences({ codeHighlighting: e.target.value })}
          >
            <option value="auto">Auto</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>

        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={userPreferences.notifications}
              onChange={(e) => updatePreferences({ notifications: e.target.checked })}
            />
            Enable Notifications
          </label>
        </div>

        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={userPreferences.autoScroll}
              onChange={(e) => updatePreferences({ autoScroll: e.target.checked })}
            />
            Auto Scroll to Bottom
          </label>
        </div>
      </div>
    </div>
  );

  // Code Editor Modal
  const CodeEditorModal = () => (
    <div className="code-editor-modal" onClick={() => setShowCodeEditor(false)}>
      <div className="code-editor-content" onClick={(e) => e.stopPropagation()}>
        <div className="code-editor-header">
          <h3>Code Editor</h3>
          <button className="close-editor" onClick={() => setShowCodeEditor(false)}>✕</button>
        </div>
        <textarea
          className="code-editor-textarea"
          value={codeEditorContent}
          onChange={(e) => setCodeEditorContent(e.target.value)}
          placeholder="// Write your code here..."
        />
        <div className="code-editor-actions">
          <button onClick={() => insertCode(codeEditorContent)}>Insert Code</button>
          <button onClick={() => setCodeEditorContent('')}>Clear</button>
        </div>
      </div>
    </div>
  );

  // History Panel
  const HistoryPanel = () => (
    <div className="history-panel" onClick={() => setShowHistory(false)}>
      <div className="history-content" onClick={(e) => e.stopPropagation()}>
        <div className="history-header">
          <h3>Conversation History</h3>
          <button className="close-history" onClick={() => setShowHistory(false)}>✕</button>
        </div>
        <div className="history-list">
          <p>No conversation history available yet.</p>
        </div>
      </div>
    </div>
  );


  // Tour Component
  const Tour = () => (
    <div className="tour-overlay" onClick={() => setShowTour(false)}>
      <div className="tour-content" onClick={(e) => e.stopPropagation()}>
        <div className="tour-step">
          <h3>{tourSteps[0].title}</h3>
          <p>{tourSteps[0].content}</p>
          <div className="tour-navigation">
            <button onClick={() => setShowTour(false)}>Skip</button>
            <button onClick={() => setShowTour(false)}>Got it!</button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="app">
      {/* Sidebar with commands */}
      <div className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-title-container">
            <div className="logo" title="Codeius Logo"></div>
            <h2>Codeius AI</h2>
          </div>
          <button
            className="menu-btn-small"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            {sidebarOpen ? '✕' : '☰'}
          </button>
        </div>

        <div className="sidebar-menu">
          <div className="menu-section">
            <h3>Quick Actions</h3>
            <div className="quick-action-item" onClick={() => runCommand("/help")}>
              <span className="action-icon">❓</span>
              <span className="action-text">Help & Support</span>
            </div>
            <div className="quick-action-item" onClick={() => runCommand("/models")}>
              <span className="action-icon">🧠</span>
              <span className="action-text">Models</span>
            </div>
            <div className="quick-action-item" onClick={() => runCommand("/clear")}>
              <span className="action-icon">🗑️</span>
              <span className="action-text">Clear Chat</span>
            </div>
          </div>

          <div className="menu-section">
            <h3>AI Commands</h3>
            {commands.map((cmd, index) => (
              <div
                key={index}
                className="command-item"
                onClick={() => runCommand(cmd.name)}
                title={cmd.description}
              >
                <div className="command-name-container">
                  <span className="command-name-icon">🤖</span>
                  <span className="command-name">{cmd.name}</span>
                </div>
                <span className="command-desc">{cmd.description}</span>
              </div>
            ))}
          </div>

          <div className="menu-section">
            <h3>Development Tools</h3>
            <div className="command-item" onClick={() => runCommand("/context")}>
              <span className="command-name">/context</span>
              <span className="command-desc">Show project context</span>
            </div>
            <div className="command-item" onClick={() => runCommand("/search")}>
              <span className="command-name">/search [query]</span>
              <span className="command-desc">Search codebase</span>
            </div>
            <div className="command-item" onClick={() => runCommand("/security_scan")}>
              <span className="command-name">/security_scan</span>
              <span className="command-desc">Run security check</span>
            </div>
            <div className="command-item" onClick={() => runCommand("/analyze")}>
              <span className="command-name">/analyze</span>
              <span className="command-desc">Analyze project</span>
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="current-model-info">
            <span className="model-label">Current Model:</span>
            <select
              value={currentModel}
              onChange={(e) => runCommand(`/switch ${e.target.value}`)}
              className="model-select-sidebar"
            >
              {Object.entries(availableModels).map(([key, model]) => (
                <option key={key} value={key}>
                  {model.name}
                </option>
              ))}
            </select>
          </div>
          <div className="sidebar-status">
            <div className="status-indicator online"></div>
            <span>Connected</span>
          </div>
        </div>
      </div>

      {/* Main chat content */}
      <div className="chat-container">
        <header className="chat-header">
          <button
            className="menu-btn"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            ☰
          </button>
          <div className="chat-title">
            <div className="logo-small" title="Codeius Logo"></div>
          </div>
          <div className="header-actions">
            <button
              className="settings-btn"
              onClick={() => setShowSettings(true)}
              title="Settings"
            >
              ⚙️
            </button>
            <button
              className="history-btn"
              onClick={() => setShowHistory(true)}
              title="History"
            >
              📜
            </button>
            <button className="control-btn">−</button>
            <button className="control-btn">□</button>
            <button className="control-btn">×</button>
          </div>
        </header>

        <div className="quick-actions">
          {quickActions.map((action, index) => (
            <button
              key={index}
              className="quick-action-btn"
              onClick={() => setInputValue(action.prompt)}
            >
              <span className="quick-action-icon">{action.icon}</span>
              <span>{action.title}</span>
            </button>
          ))}
        </div>

        <div className="messages-container">
          {messages.map((message) => (
            <div key={message.id} className={`message ${message.sender}`}>
              <div className="message-content">
                <div className="message-text">
                  {message.content.split('\n').map((line, i) => (
                    <div key={i}>{line}</div>
                  ))}
                </div>
                <div className="message-timestamp">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message ai">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form id="message-form" onSubmit={handleFormSubmit} className="input-form">
          <div className="input-container">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask Codeius anything about coding..."
              className="message-input"
              disabled={isLoading}
              autoFocus
            />
            <button
              type="submit"
              className="send-button"
              disabled={!inputValue.trim() || isLoading}
            >
              {isLoading ? 'Sending...' : '➤'}
            </button>
          </div>
          <div className="input-hint">
            <span>Tip: Use /commands to see available commands</span>
          </div>
        </form>
      </div>

      {/* Settings Panel */}
      {showSettings && <SettingsPanel />}

      {/* Code Editor Modal */}
      {showCodeEditor && <CodeEditorModal />}

      {/* History Panel */}
      {showHistory && <HistoryPanel />}

      {/* Tour Modal */}
      {showTour && <Tour />}

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
}

export default App;