import React, { useState, useRef, useEffect } from 'react';
import { exportToPDF, exportToHTML, exportCodeToZip } from '../../utils/exportUtils';
import { useToast } from '../Toast/ToastContainer';
import './ExportMenu.css';

const ExportMenu = ({ messages, elementId }) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  const toast = useToast();

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleExport = async (type) => {
    setIsOpen(false);
    try {
      if (type === 'pdf') {
        await exportToPDF(elementId);
        toast.success('PDF Exported successfully!');
      } else if (type === 'html') {
        exportToHTML(messages);
        toast.success('HTML Exported successfully!');
      } else if (type === 'zip') {
        await exportCodeToZip(messages);
        toast.success('Code Snippets Exported successfully!');
      } else if (type === 'share') {
        // Assuming sessionId is available or we use the current one
        // For now, we'll fetch it from localStorage or props if passed
        // This is a simplified example
        const sessionId = localStorage.getItem('currentSessionId') || 'default';
        const response = await fetch(`http://localhost:5000/api/sessions/${sessionId}/share`, { method: 'POST' });
        const data = await response.json();
        
        if (data.share_url) {
          await navigator.clipboard.writeText(data.share_url);
          toast.success('Link copied to clipboard!');
        } else {
          throw new Error('Failed to generate link');
        }
      }
    } catch (error) {
      console.error(error);
      toast.error(`Action failed: ${error.message}`);
    }
  };

  return (
    <div className="export-menu-container" ref={menuRef}>
      <button 
        className="export-button" 
        onClick={() => setIsOpen(!isOpen)}
        title="Export & Share"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path>
          <polyline points="16 6 12 2 8 6"></polyline>
          <line x1="12" y1="2" x2="12" y2="15"></line>
        </svg>
        Share / Export
      </button>

      {isOpen && (
        <div className="export-dropdown">
          <div className="export-item" onClick={() => handleExport('share')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="export-icon">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
            </svg>
            Share via Link
          </div>
          <div className="divider" style={{margin: '4px 0', borderBottom: '1px solid #3e3e42'}}></div>
          <div className="export-item" onClick={() => handleExport('pdf')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="export-icon">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            Export as PDF
          </div>
          <div className="export-item" onClick={() => handleExport('html')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="export-icon">
              <polyline points="16 18 22 12 16 6"></polyline>
              <polyline points="8 6 2 12 8 18"></polyline>
            </svg>
            Export as HTML
          </div>
          <div className="export-item" onClick={() => handleExport('zip')}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="export-icon">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
            Export Code (ZIP)
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportMenu;
