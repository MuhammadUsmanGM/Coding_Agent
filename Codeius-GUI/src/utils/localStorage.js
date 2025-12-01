// localStorage utility for chat persistence

const STORAGE_KEYS = {
  SESSIONS: 'codeius_sessions', // Stores metadata: [{id, title, lastModified, preview}]
  CURRENT_SESSION_ID: 'codeius_current_session_id',
  SETTINGS: 'codeius_settings',
};

// Generate a unique ID
const generateId = () => '_' + Math.random().toString(36).substr(2, 9);

// Get all sessions metadata
export const getSessions = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.SESSIONS);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Failed to load sessions:', error);
    return [];
  }
};

// Get a specific session's messages
export const getSessionMessages = (sessionId) => {
  try {
    const stored = localStorage.getItem(`codeius_session_${sessionId}`);
    if (stored) {
      const messages = JSON.parse(stored);
      return messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }));
    }
  } catch (error) {
    console.error(`Failed to load messages for session ${sessionId}:`, error);
  }
  return null;
};

// Save messages to the current session
export const saveSessionMessages = (sessionId, messages) => {
  try {
    if (!sessionId) return;
    
    // Save the messages
    localStorage.setItem(`codeius_session_${sessionId}`, JSON.stringify(messages));

    // Update session metadata (preview, timestamp)
    const sessions = getSessions();
    const sessionIndex = sessions.findIndex(s => s.id === sessionId);
    
    // Determine title/preview from first user message
    const firstUserMsg = messages.find(m => m.sender === 'user');
    const preview = firstUserMsg ? firstUserMsg.text.substring(0, 50) : 'New Chat';
    const title = firstUserMsg ? firstUserMsg.text.substring(0, 30) : 'New Chat';

    const sessionData = {
      id: sessionId,
      title: title,
      preview: preview,
      lastModified: new Date().toISOString(),
      messageCount: messages.length
    };

    if (sessionIndex >= 0) {
      sessions[sessionIndex] = sessionData;
    } else {
      sessions.unshift(sessionData); // Add new session to top
    }

    localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(sessions));
  } catch (error) {
    console.error('Failed to save session messages:', error);
  }
};

// Create a new session
export const createNewSession = () => {
  const newId = generateId();
  localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION_ID, newId);
  return newId;
};

// Get current session ID
export const getCurrentSessionId = () => {
  let id = localStorage.getItem(STORAGE_KEYS.CURRENT_SESSION_ID);
  if (!id) {
    id = createNewSession();
  }
  return id;
};

// Set current session ID
export const setCurrentSessionId = (id) => {
  localStorage.setItem(STORAGE_KEYS.CURRENT_SESSION_ID, id);
};

// Delete a session
export const deleteSession = (sessionId) => {
  try {
    // Remove messages
    localStorage.removeItem(`codeius_session_${sessionId}`);
    
    // Remove from metadata
    const sessions = getSessions().filter(s => s.id !== sessionId);
    localStorage.setItem(STORAGE_KEYS.SESSIONS, JSON.stringify(sessions));
    
    // If deleted current session, clear current ID
    if (getCurrentSessionId() === sessionId) {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_SESSION_ID);
    }
  } catch (error) {
    console.error('Failed to delete session:', error);
  }
};

// Clear all history
export const clearAllHistory = () => {
  try {
    const sessions = getSessions();
    sessions.forEach(s => localStorage.removeItem(`codeius_session_${s.id}`));
    localStorage.removeItem(STORAGE_KEYS.SESSIONS);
    localStorage.removeItem(STORAGE_KEYS.CURRENT_SESSION_ID);
  } catch (error) {
    console.error('Failed to clear all history:', error);
  }
};

// Save settings
export const saveSettings = (settings) => {
  try {
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
  } catch (error) {
    console.error('Failed to save settings:', error);
  }
};

// Load settings
export const loadSettings = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    return stored ? JSON.parse(stored) : {};
  } catch (error) {
    console.error('Failed to load settings:', error);
    return {};
  }
};

// Export conversation as Markdown
export const exportAsMarkdown = (messages, conversationName = 'Conversation') => {
  let markdown = `# ${conversationName}\n\n`;
  markdown += `*Exported on ${new Date().toLocaleString()}*\n\n---\n\n`;

  messages.forEach(msg => {
    const sender = msg.sender === 'user' ? '**You**' : msg.sender === 'ai' ? '**Codeius AI**' : '**System**';
    const time = msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    markdown += `### ${sender} (${time})\n\n`;
    markdown += `${msg.text}\n\n---\n\n`;
  });

  return markdown;
};

// Download markdown file
export const downloadMarkdown = (content, filename = 'conversation.md') => {
  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// Legacy support functions to prevent breaking changes during migration
export const loadMessages = () => getSessionMessages(getCurrentSessionId());
export const saveMessages = (msgs) => saveSessionMessages(getCurrentSessionId(), msgs);
