import React, { useEffect, useRef } from 'react';
import Fuse from 'fuse.js';
import './CommandAutocomplete.css';

const CommandAutocomplete = ({ commands, query, onSelect, onClose, position }) => {
  const listRef = useRef(null);
  const [selectedIndex, setSelectedIndex] = React.useState(0);

  // Fuzzy search configuration
  const fuse = new Fuse(commands, {
    keys: ['cmd', 'desc'],
    threshold: 0.4,
    includeScore: true,
  });

  // Filter commands based on query
  const filteredCommands = query.length > 1
    ? fuse.search(query.slice(1)).map(result => result.item)
    : commands;

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter' && filteredCommands.length > 0) {
        e.preventDefault();
        onSelect(filteredCommands[selectedIndex].cmd);
      } else if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [filteredCommands, selectedIndex, onSelect, onClose]);

  // Scroll selected item into view
  useEffect(() => {
    if (listRef.current) {
      const selectedElement = listRef.current.children[selectedIndex];
      if (selectedElement) {
        selectedElement.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }
    }
  }, [selectedIndex]);

  if (filteredCommands.length === 0) {
    return null;
  }

  return (
    <div className="autocomplete-container" style={{ bottom: position?.bottom || '70px' }}>
      <div className="autocomplete-header">
        <span>Commands</span>
        <span className="autocomplete-hint">↑↓ Navigate • Enter Select • Esc Close</span>
      </div>
      <ul className="autocomplete-list" ref={listRef}>
        {filteredCommands.slice(0, 8).map((command, index) => (
          <li
            key={command.cmd}
            className={`autocomplete-item ${index === selectedIndex ? 'selected' : ''}`}
            onClick={() => onSelect(command.cmd)}
            onMouseEnter={() => setSelectedIndex(index)}
          >
            <div className="autocomplete-cmd">{command.cmd}</div>
            <div className="autocomplete-desc">{command.desc}</div>
          </li>
        ))}
      </ul>
      {filteredCommands.length > 8 && (
        <div className="autocomplete-footer">
          +{filteredCommands.length - 8} more commands
        </div>
      )}
    </div>
  );
};

export default CommandAutocomplete;
