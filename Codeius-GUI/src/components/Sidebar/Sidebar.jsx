import React, { useState, useEffect, useRef } from 'react';
import './Sidebar.css';

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const isOpenRef = useRef(isOpen); // Use ref to track current state in event handlers

  const commands = [
    { cmd: '/models', desc: 'List all available AI models' },
    { cmd: '/mcp', desc: 'List available MCP tools' },
    { cmd: '/dashboard', desc: 'Show real-time code quality dashboard' },
    { cmd: '/themes', desc: 'Show available visual themes' },
    { cmd: '/add_model', desc: 'Add a custom AI model with API key and endpoint' },
    { cmd: '/shell [command]', desc: 'Execute a direct shell command securely' },
    { cmd: '/toggle', desc: 'Toggle between Interaction and Shell modes' },
    { cmd: '/mode', desc: 'Alternative command for toggling modes' },
    { cmd: '/keys', desc: 'Show mode switching options' },
    { cmd: '/shortcuts', desc: 'Show mode switching options' },
    { cmd: '/ocr [image_path]', desc: 'Extract text from an image using OCR' },
    { cmd: '/refactor [file_path]', desc: 'Analyze and refactor code in a file' },
    { cmd: '/diff [file1] [file2]', desc: 'Compare two files or directories' },
    { cmd: '/scaffold [name] [template]', desc: 'Generate project scaffolding' },
    { cmd: '/env [action] [variables]', desc: 'Manage environment files' },
    { cmd: '/rename [old] [new] [file]', desc: 'Batch rename variables' },
    { cmd: '/plot [metric]', desc: 'Plot code metrics and data' },
    { cmd: '/update_docs [type] [args]', desc: 'Update documentation files' },
    { cmd: '/snippet [action] [args]', desc: 'Manage code snippets' },
    { cmd: '/scrape [file_or_dir_or_url] [css_selector]', desc: 'Scrape web content' },
    { cmd: '/config [action] [args]', desc: 'Manage configurations' },
    { cmd: '/schedule [task_type] [interval] [target]', desc: 'Schedule tasks to run automatically' },
    { cmd: '/inspect [package]', desc: 'Inspect package information' },
    { cmd: '/context', desc: 'Show current project context information' },
    { cmd: '/set_project [path] [name]', desc: 'Set the current project context' },
    { cmd: '/search [query]', desc: 'Semantic search across the codebase' },
    { cmd: '/find_function [name]', desc: 'Find a function by name' },
    { cmd: '/find_class [name]', desc: 'Find a class by name' },
    { cmd: '/file_context [file_path]', desc: 'Show context for a specific file' },
    { cmd: '/autodetect', desc: 'Auto-detect and set project context' },
    { cmd: '/security_scan', desc: 'Run comprehensive security scan' },
    { cmd: '/secrets_scan', desc: 'Scan for secrets and sensitive information' },
    { cmd: '/vuln_scan', desc: 'Scan for code vulnerabilities' },
    { cmd: '/policy_check', desc: 'Check for policy violations' },
    { cmd: '/security_policy', desc: 'Show current security policy settings' },
    { cmd: '/security_report', desc: 'Generate comprehensive security report' },
    { cmd: '/set_policy [key] [value]', desc: 'Update security policy setting' },
    { cmd: '/plugins', desc: 'List available plugins' },
    { cmd: '/create_plugin [name]', desc: 'Create a new plugin skeleton' },
    { cmd: '/switch [model_key]', desc: 'Switch to a specific model' },
    { cmd: '/gen_viz', desc: 'Generate all project visualizations' },
    { cmd: '/dep_graph', desc: 'Show dependency graph visualization' },
    { cmd: '/proj_struct', desc: 'Show project structure visualization' },
    { cmd: '/perf_dash', desc: 'Show performance metrics dashboard' },
    { cmd: '/performance', desc: 'Show performance metrics dashboard' },
    { cmd: '/viz_summary', desc: 'Show analysis summary dashboard' },
    { cmd: '/analyze', desc: 'Analyze the current project structure and content' },
    { cmd: '/run_test [file_path]', desc: 'Run a specific test file' },
    { cmd: '/test', desc: 'Run all tests' },
    { cmd: '/help', desc: 'Show help message' },
    { cmd: '/clear', desc: 'Clear the conversation history' },
    { cmd: '/exit', desc: 'Exit the application' }
  ];

  const toggleSidebar = () => {
    const sidebarElement = document.querySelector('.sidebar');
    const isOpen = sidebarElement?.classList.contains('open');

    if (isOpen) {
      // Remove both classes when closing
      sidebarElement?.classList.remove('open');
      document.body.classList.remove('sidebar-open');
      setIsOpen(false);
      isOpenRef.current = false;
    } else {
      // Add both classes for opening
      sidebarElement?.classList.add('open');
      document.body.classList.add('sidebar-open');
      setIsOpen(true);
      isOpenRef.current = true;
    }
  };

  const closeSidebar = () => {
    const sidebarElement = document.querySelector('.sidebar');
    // Remove both classes when closing
    sidebarElement?.classList.remove('open');
    document.body.classList.remove('sidebar-open');
    setIsOpen(false);
    isOpenRef.current = false;
  };

  // Function to handle command click and pass it to input
  const handleCommandClick = (commandText) => {
    // Find the input field and set its value
    const inputField = document.querySelector('.input-field');
    if (inputField) {
      // Set the value to the clicked command
      inputField.value = commandText;

      // Trigger the input event to update the React state
      const event = new Event('input', { bubbles: true });
      inputField.dispatchEvent(event);

      // Optionally, you could also focus on the input field
      inputField.focus();
    }
  };

  useEffect(() => {
    // Update ref when state changes
    isOpenRef.current = isOpen;

    // Track mouse movement to show edge trigger
    const handleMouseMove = (e) => {
      const edgeTrigger = document.getElementById('sidebar-edge-trigger');
      if (!edgeTrigger) return;

      // Use the ref value to check if sidebar is open
      // Show the trigger if mouse is near the left edge (within 20px) and sidebar is closed
      if (e.clientX <= 20 && !isOpenRef.current) {
        edgeTrigger.style.opacity = '1';
        edgeTrigger.style.transform = 'translateX(0)';
      } else if (e.clientX > 40 || isOpenRef.current) {
        // Hide the trigger if mouse is not near the edge or sidebar is open
        edgeTrigger.style.opacity = '0';
        edgeTrigger.style.transform = 'translateX(-50%)';
      }
    };

    document.addEventListener('mousemove', handleMouseMove);

    // Set initial state based on class on sidebar element
    const sidebarElement = document.querySelector('.sidebar');
    if (sidebarElement?.classList.contains('open')) {
      setIsOpen(true);
      isOpenRef.current = true;
      document.body.classList.add('sidebar-open');
    } else {
      setIsOpen(false);
      isOpenRef.current = false;
    }

    // Listen for changes to the sidebar open state
    const handleSidebarToggle = () => {
      const isOpenNow = sidebarElement?.classList.contains('open');
      setIsOpen(isOpenNow);
      isOpenRef.current = isOpenNow;
      if (isOpenNow) {
        document.body.classList.add('sidebar-open');
      } else {
        document.body.classList.remove('sidebar-open');
      }
    };

    // Create a MutationObserver to watch for class changes
    const observer = new MutationObserver(handleSidebarToggle);

    if (sidebarElement) {
      observer.observe(sidebarElement, {
        attributes: true,
        attributeFilter: ['class']
      });
    }

    // Set up click handler for backdrop
    const handleClickOutside = (event) => {
      const sidebar = document.querySelector('.sidebar');
      const inputField = event.target.closest('.input-field') ||
                        event.target.classList.contains('input-container') ||
                        event.target.classList.contains('input-field');

      if (isOpenRef.current &&
          sidebar &&
          !sidebar.contains(event.target) &&
          !inputField && // Don't close if clicking on input field
          !event.target.classList.contains('sidebar-backdrop') &&
          !event.target.classList.contains('sidebar-close-btn')) {
        // Close sidebar if clicked outside (but not on input field)
        sidebar.classList.remove('open');
        document.body.classList.remove('sidebar-open');
        setIsOpen(false);
        isOpenRef.current = false;
      }
    };

    document.addEventListener('click', handleClickOutside);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      observer.disconnect();
      document.removeEventListener('click', handleClickOutside);
    };
  }, []);

  return (
    <>
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <img src="/favicon.png" alt="Codeius AI Logo" className="sidebar-logo" />
          <h2 className="sidebar-title">Codeius Commands</h2>
          <button 
            className="sidebar-close-btn" 
            onClick={closeSidebar}
            aria-label="Close sidebar"
          >
            ×
          </button>
        </div>
        
        <div className="sidebar-content">
          <div className="commands-list">
            {commands.map((command, index) => (
              <div
                key={index}
                className="command-item"
                onClick={() => handleCommandClick(command.cmd)}
                style={{ cursor: 'pointer' }}
              >
                <div className="command-header">
                  <span className="command-cmd">{command.cmd}</span>
                </div>
                <div className="command-desc">{command.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Edge trigger that appears when mouse is near left edge */}
      <button
        id="sidebar-edge-trigger"
        className="sidebar-edge-trigger"
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();

          // Use setTimeout to ensure the DOM is ready
          setTimeout(() => {
            const sidebarElement = document.querySelector('.sidebar');
            if (sidebarElement) {
              // Ensure it's not already open
              if (!sidebarElement.classList.contains('open')) {
                sidebarElement.classList.add('open');
                document.body.classList.add('sidebar-open');
                setIsOpen(true);
                isOpenRef.current = true;
              }
            } else {
              console.error('Sidebar element not found');
            }
          }, 0);
        }}
        aria-label="Open sidebar"
      >
        <span className="trigger-line"></span>
        <span className="trigger-line"></span>
        <span className="trigger-line"></span>
      </button>
      
      {isOpen && <div className="sidebar-backdrop" />}
    </>
  );
};

export default Sidebar;