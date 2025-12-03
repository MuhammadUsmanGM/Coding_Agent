/**
 * Time utility functions for better UX
 */

/**
 * Convert timestamp to relative time string (e.g., "2m ago", "1h ago")
 * @param {Date|string|number} timestamp - The timestamp to convert
 * @returns {string} Relative time string
 */
export const getRelativeTime = (timestamp) => {
  const now = new Date();
  const then = new Date(timestamp);
  const seconds = Math.floor((now - then) / 1000);
  
  if (seconds < 0) return 'just now'; // Future dates
  if (seconds < 60) return 'just now';
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
  if (seconds < 2592000) return `${Math.floor(seconds / 604800)}w ago`;
  
  return then.toLocaleDateString();
};

/**
 * Format timestamp to full readable string
 * @param {Date|string|number} timestamp - The timestamp to format
 * @returns {string} Formatted timestamp
 */
export const formatFullTime = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Update relative times periodically
 * @param {Function} updateFn - Function to call on update
 * @returns {number} Interval ID for cleanup
 */
export const startTimeUpdater = (updateFn) => {
  return setInterval(updateFn, 60000); // Update every minute
};
