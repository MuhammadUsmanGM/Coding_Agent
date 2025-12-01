// src/services/git.js

/**
 * API functions for Git operations
 */

const API_BASE_URL = '/api';

/**
 * Get git status of the current repository
 * @returns {Promise<Object>}
 */
export const getGitStatus = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/git/status`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Git status error:', error);
    throw error;
  }
};

/**
 * Add files to git staging area
 * @param {Array<string>|string} files - Files to add
 * @returns {Promise<Object>}
 */
export const gitAdd = async (files) => {
  try {
    const response = await fetch(`${API_BASE_URL}/git/add`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ files }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Git add error:', error);
    throw error;
  }
};

/**
 * Commit staged changes
 * @param {string} message - Commit message
 * @returns {Promise<Object>}
 */
export const gitCommit = async (message) => {
  try {
    const response = await fetch(`${API_BASE_URL}/git/commit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Git commit error:', error);
    throw error;
  }
};

/**
 * Push changes to remote repository
 * @param {string} remote - Remote name (default: origin)
 * @param {string} branch - Branch name (default: main)
 * @returns {Promise<Object>}
 */
export const gitPush = async (remote = 'origin', branch = 'main') => {
  try {
    const response = await fetch(`${API_BASE_URL}/git/push`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ remote, branch }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Git push error:', error);
    throw error;
  }
};

/**
 * Pull changes from remote repository
 * @param {string} remote - Remote name (default: origin)
 * @param {string} branch - Branch name (default: main)
 * @returns {Promise<Object>}
 */
export const gitPull = async (remote = 'origin', branch = 'main') => {
  try {
    const response = await fetch(`${API_BASE_URL}/git/pull`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ remote, branch }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Git pull error:', error);
    throw error;
  }
};

/**
 * Clone a remote repository
 * @param {string} url - Repository URL
 * @param {string} destination - Destination path
 * @returns {Promise<Object>}
 */
export const gitClone = async (url, destination = null) => {
  try {
    const response = await fetch(`${API_BASE_URL}/git/clone`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, destination }),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Git clone error:', error);
    throw error;
  }
};

/**
 * Manage git branches
 * @param {'create'|'switch'|null} create - Name of branch to create
 * @param {'switch'|'create'|null} switchTo - Name of branch to switch to
 * @returns {Promise<Object>}
 */
export const gitBranch = async (create = null, switchTo = null) => {
  try {
    const payload = {};
    if (create) payload.create = create;
    if (switchTo) payload.switch = switchTo;

    const response = await fetch(`${API_BASE_URL}/git/branch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Git branch error:', error);
    throw error;
  }
};

/**
 * Get git commit history
 * @param {number} limit - Number of commits to return
 * @returns {Promise<Object>}
 */
export const gitLog = async (limit = 10) => {
  try {
    const response = await fetch(`${API_BASE_URL}/git/log?limit=${limit}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Git log error:', error);
    throw error;
  }
};