const API_BASE = 'http://localhost:8080/api';

// Helper function for delays
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// Retry mechanism for API calls
const apiCallWithRetry = async (url, options = {}, retries = 3) => {
  let lastError;
  
  for (let i = 0; i <= retries; i++) {
    try {
      const response = await fetch(url, options);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      lastError = error;
      
      if (i < retries) {
        // Exponential backoff: wait 1s, 2s, 4s
        const waitTime = Math.pow(2, i) * 1000;
        console.log(`Request failed, retrying in ${waitTime}ms... (${i + 1}/${retries})`);
        await sleep(waitTime);
      }
    }
  }
  
  throw lastError;
};

// Send message to AI
export const sendMessage = async (prompt) => {
  return apiCallWithRetry(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt })
  });
};

// Execute shell command
export const executeShellCommand = async (command) => {
  return apiCallWithRetry(`${API_BASE}/shell`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command })
  });
};

// Get current working directory
export const getCwd = async () => {
  try {
    const response = await apiCallWithRetry(`${API_BASE}/cwd`);
    return response.cwd;
  } catch (error) {
    console.error('Failed to get CWD:', error);
    return '/';
  }
};

// Get available models
export const getModels = async () => {
  try {
    return await apiCallWithRetry(`${API_BASE}/models`);
  } catch (error) {
    console.error('Failed to get models:', error);
    return {};
  }
};

// Switch model
export const switchModel = async (modelId) => {
  return apiCallWithRetry(`${API_BASE}/switch_model`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model_id: modelId })
  });
};

// Clear chat history
export const clearHistory = async () => {
  return apiCallWithRetry(`${API_BASE}/clear_history`, {
    method: 'POST'
  });
};

// Upload file
export const uploadFile = async (formData) => {
  try {
    const response = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Upload failed');
    }
    
    return await response.json();
  } catch (error) {
    console.error('File upload error:', error);
    throw error;
  }
};

// Get uploaded files for current session
export const getUploadedFiles = async () => {
  try {
    return await apiCallWithRetry(`${API_BASE}/files`);
  } catch (error) {
    console.error('Failed to get uploaded files:', error);
    return [];
  }
};

// Delete uploaded file
export const deleteUploadedFile = async (filename) => {
  return apiCallWithRetry(`${API_BASE}/files/${encodeURIComponent(filename)}`, {
    method: 'DELETE'
  });
};

// Health check
export const getFiles = async (path = '.') => {
  try {
    const response = await fetch(`${API_BASE}/files?path=${encodeURIComponent(path)}`);
    if (!response.ok) throw new Error('Failed to fetch files');
    const data = await response.json();
    return data.files;
  } catch (error) {
    console.error('Error fetching files:', error);
    return [];
  }
};

export const shareSession = async (sessionId) => {
  try {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/share`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to share session');
    const data = await response.json();
    return data.share_url;
  } catch (error) {
    console.error('Error sharing session:', error);
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    await fetch(`${API_BASE}/health`);
    return true;
  } catch {
    return false;
  }
};
