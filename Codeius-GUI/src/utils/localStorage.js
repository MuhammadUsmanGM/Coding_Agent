// localStorage utility for chat persistence

const STORAGE_KEYS = {
  MESSAGES: 'codeius_messages',
  CONVERSATIONS: 'codeius_conversations',
  CURRENT_CONVERSATION: 'codeius_current_conversation',
  SETTINGS: 'codeius_settings',
};

// Save messages to localStorage
export const saveMessages = (messages) => {
  try {
    localStorage.setItem(STORAGE_KEYS.MESSAGES, JSON.stringify(messages));
  } catch (error) {
    console.error('Failed to save messages:', error);
  }
};

// Load messages from localStorage
export const loadMessages = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.MESSAGES);
    if (stored) {
      const messages = JSON.parse(stored);
      // Convert timestamp strings back to Date objects
      return messages.map(msg => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      }));
    }
  } catch (error) {
    console.error('Failed to load messages:', error);
  }
  return null;
};

// Save a conversation
export const saveConversation = (name, messages) => {
  try {
    const conversations = loadConversations();
    const conversation = {
      id: Date.now(),
      name,
      messages,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    conversations.push(conversation);
    localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
    return conversation;
  } catch (error) {
    console.error('Failed to save conversation:', error);
    return null;
  }
};

// Load all conversations
export const loadConversations = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Failed to load conversations:', error);
    return [];
  }
};

// Delete a conversation
export const deleteConversation = (id) => {
  try {
    const conversations = loadConversations();
    const filtered = conversations.filter(conv => conv.id !== id);
    localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('Failed to delete conversation:', error);
    return false;
  }
};

// Load a specific conversation
export const loadConversation = (id) => {
  try {
    const conversations = loadConversations();
    const conversation = conversations.find(conv => conv.id === id);
    if (conversation) {
      // Convert timestamp strings back to Date objects
      return {
        ...conversation,
        messages: conversation.messages.map(msg => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
      };
    }
  } catch (error) {
    console.error('Failed to load conversation:', error);
  }
  return null;
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
  let markdown = `# ${conversationName}\\n\\n`;
  markdown += `*Exported on ${new Date().toLocaleString()}*\\n\\n---\\n\\n`;

  messages.forEach(msg => {
    const sender = msg.sender === 'user' ? '**You**' : msg.sender === 'ai' ? '**Codeius AI**' : '**System**';
    const time = msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    markdown += `### ${sender} (${time})\\n\\n`;
    markdown += `${msg.text}\\n\\n---\\n\\n`;
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
