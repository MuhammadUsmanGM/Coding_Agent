const API_BASE_URL = '/api';

/**
 * Sends a prompt to the AI assistant.
 * @param {string} prompt - The user's message.
 * @returns {Promise<string>} - The AI's response.
 */
export const sendMessage = async (prompt) => {
  try {
    const response = await fetch(`${API_BASE_URL}/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to get response');
    }

    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * Checks if the backend server is running.
 * @returns {Promise<boolean>}
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch (error) {
    return false;
  }
};

/**
 * Gets the current working directory from the server.
 * @returns {Promise<string>}
 */
export const getCwd = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/cwd`);
    const data = await response.json();
    return data.cwd;
  } catch (error) {
    console.error('Failed to get CWD:', error);
    return '';
  }
};

/**
 * Executes a shell command on the server.
 * @param {string} command - The command to execute.
 * @returns {Promise<object>} - The command result.
 */
export const executeShellCommand = async (command) => {
  try {
    const response = await fetch(`${API_BASE_URL}/shell`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ command }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Shell command error:', error);
    throw error;
  }
};

/**
 * Gets available AI models.
 * @returns {Promise<object>}
 */
export const getModels = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/models`);
    const data = await response.json();
    return data.models;
  } catch (error) {
    console.error('Failed to get models:', error);
    return {};
  }
};

/**
 * Switches the active AI model.
 * @param {string} modelKey - The key of the model to switch to.
 * @returns {Promise<string>} - Result message.
 */
export const switchModel = async (modelKey) => {
  try {
    const response = await fetch(`${API_BASE_URL}/switch_model`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ model_key: modelKey }),
    });

    const data = await response.json();
    if (data.error) throw new Error(data.error);
    return data.result;
  } catch (error) {
    console.error('Switch model error:', error);
    throw error;
  }
};

/**
 * Clears the conversation history on the server.
 * @returns {Promise<string>}
 */
export const clearHistory = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/clear_history`, {
      method: 'POST',
    });

    const data = await response.json();
    if (data.error) throw new Error(data.error);
    return data.result;
  } catch (error) {
    console.error('Clear history error:', error);
    throw error;
  }
};
