import React, { useState, useEffect, useRef } from 'react';
import Fuse from 'fuse.js';
import { getRelativeTime } from '../../utils/timeUtils';
import './SearchModal.css';

const SearchModal = ({ isOpen, onClose, messages, onSelectMessage }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [filter, setFilter] = useState('all'); // all, user, ai, code
  const [isSearching, setIsSearching] = useState(false);
  const inputRef = useRef(null);

  // Initialize Fuse.js for local search
  const fuse = new Fuse(messages, {
    keys: ['text'],
    threshold: 0.4,
    includeMatches: true
  });

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setQuery('');
      setResults([]);
    }
  }, [isOpen]);

  // Handle search
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const performSearch = async () => {
      setIsSearching(true);
      
      // 1. Local Search (Current Session)
      let localResults = fuse.search(query).map(result => ({
        ...result.item,
        matches: result.matches,
        source: 'current'
      }));

      // 2. Global Search (Backend) - Debounced in a real app
      try {
        const response = await fetch(`http://localhost:5000/api/search?q=${encodeURIComponent(query)}&limit=10`);
        if (response.ok) {
          const globalResults = await response.json();
          // Filter out duplicates from current session if needed
          // For now, just append
          
          // Combine results
          const combined = [...localResults];
          
          // Add global results that aren't in local
          globalResults.forEach(gr => {
            if (!combined.find(lr => lr.id === gr.id)) {
              combined.push({
                ...gr,
                source: 'history'
              });
            }
          });
          
          // Apply filters
          const filtered = combined.filter(item => {
            if (filter === 'all') return true;
            if (filter === 'user') return item.sender === 'user';
            if (filter === 'ai') return item.sender === 'ai' || item.sender === 'assistant';
            if (filter === 'code') return item.text.includes('```');
            return true;
          });

          setResults(filtered);
        }
      } catch (error) {
        console.error("Search failed:", error);
        setResults(localResults); // Fallback to local only
      } finally {
        setIsSearching(false);
      }
    };

    const debounceTimer = setTimeout(performSearch, 300);
    return () => clearTimeout(debounceTimer);
  }, [query, filter, messages]);

  // Keyboard navigation
  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (results[selectedIndex]) {
        handleSelect(results[selectedIndex]);
      }
    } else if (e.key === 'Escape') {
      onClose();
    }
  };

  const handleSelect = (item) => {
    onSelectMessage(item);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="search-modal-overlay" onClick={onClose}>
      <div className="search-modal" onClick={e => e.stopPropagation()}>
        <div className="search-header">
          <span className="search-icon">🔍</span>
          <input
            ref={inputRef}
            type="text"
            className="search-input"
            placeholder="Search messages, code, history..."
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
          />
          <span className="search-shortcut">Esc</span>
        </div>

        <div className="search-filters">
          <button 
            className={`filter-chip ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button 
            className={`filter-chip ${filter === 'user' ? 'active' : ''}`}
            onClick={() => setFilter('user')}
          >
            User
          </button>
          <button 
            className={`filter-chip ${filter === 'ai' ? 'active' : ''}`}
            onClick={() => setFilter('ai')}
          >
            AI
          </button>
          <button 
            className={`filter-chip ${filter === 'code' ? 'active' : ''}`}
            onClick={() => setFilter('code')}
          >
            Code
          </button>
        </div>

        <div className="search-results">
          {results.length === 0 ? (
            <div className="search-empty">
              {query ? 'No results found' : 'Type to search...'}
            </div>
          ) : (
            results.map((item, index) => (
              <div 
                key={item.id || index}
                className={`search-result-item ${index === selectedIndex ? 'selected' : ''}`}
                onClick={() => handleSelect(item)}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <div className="result-header">
                  <span className={`result-sender ${item.sender === 'user' ? 'user' : 'ai'}`}>
                    {item.sender === 'user' ? 'You' : 'Codeius'}
                  </span>
                  <span className="result-session">
                    {item.source === 'history' ? (item.session_name || 'Past Session') : 'Current Session'} • {getRelativeTime(item.timestamp)}
                  </span>
                </div>
                <div className="result-preview">
                  {/* Simple highlighting */}
                  {item.text.substring(0, 150)}{item.text.length > 150 ? '...' : ''}
                </div>
              </div>
            ))
          )}
        </div>

        <div className="search-footer">
          <span>↑↓ to navigate</span>
          <span>↵ to select</span>
        </div>
      </div>
    </div>
  );
};

export default SearchModal;
