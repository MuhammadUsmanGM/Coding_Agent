import React, { useState, useEffect } from 'react';
import './ContextPanel.css';

const ContextPanel = ({ isOpen, onClose }) => {
  const [context, setContext] = useState({
    files: [],
    git: null,
    dependencies: null,
    loading: true
  });

  useEffect(() => {
    if (isOpen) {
      loadContext();
    }
  }, [isOpen]);

  const loadContext = async () => {
    setContext(prev => ({ ...prev, loading: true }));
    
    try {
      // Load project structure
      const projectRes = await fetch('/api/project/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: '.' })
      });
      const projectData = await projectRes.json();

      // Load git status
      const gitRes = await fetch('/api/git/status');
      const gitData = await gitRes.json();

      // Load dependencies
      const depsRes = await fetch('/api/project/dependencies', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: '.' })
      });
      const depsData = await depsRes.json();

      setContext({
        files: projectData.files || [],
        git: gitData,
        dependencies: depsData,
        loading: false
      });
    } catch (error) {
      console.error('Error loading context:', error);
      setContext(prev => ({ ...prev, loading: false }));
    }
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="context-overlay" onClick={onClose} />
      <div className="context-panel">
        <div className="context-header">
          <h2>🧠 Project Context</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        {context.loading ? (
          <div className="context-loading">
            <div className="spinner"></div>
            <p>Loading project context...</p>
          </div>
        ) : (
          <div className="context-content">
            {/* Files Section */}
            <section className="context-section">
              <h3>📁 Project Files</h3>
              <div className="context-stat">
                <strong>{context.files.length}</strong> files
              </div>
              <div className="file-list">
                {context.files.slice(0, 15).map((file, idx) => (
                  <div key={idx} className="file-item">
                    <span className="file-icon">{getFileIcon(file.extension)}</span>
                    <span className="file-name">{file.path}</span>
                    <span className="file-size">{formatSize(file.size)}</span>
                  </div>
                ))}
                {context.files.length > 15 && (
                  <div className="file-item more">
                    +{context.files.length - 15} more files
                  </div>
                )}
              </div>
            </section>

            {/* Git Section */}
            {context.git && context.git.git_available !== false && (
              <section className="context-section">
                <h3>🔀 Git Status</h3>
                {context.git.has_changes ? (
                  <div className="git-status warning">
                    <span className="badge warning">⚠️ Uncommitted changes</span>
                    <pre className="git-diff">{context.git.uncommitted_diff}</pre>
                  </div>
                ) : (
                  <div className="git-status success">
                    <span className="badge success">✓ Clean working tree</span>
                  </div>
                )}
                
                {context.git.recent_commits && context.git.recent_commits.length > 0 && (
                  <div className="recent-commits">
                    <h4>Recent Commits</h4>
                    {context.git.recent_commits.map((commit, idx) => (
                      <div key={idx} className="commit-item">{commit}</div>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* Dependencies Section */}
            {context.dependencies && Object.keys(context.dependencies).length > 0 && (
              <section className="context-section">
                <h3>📦 Dependencies</h3>
                
                {context.dependencies.javascript && (
                  <div className="dep-group">
                    <h4>Node.js / JavaScript</h4>
                    <div className="dep-count">
                      {Object.keys(context.dependencies.javascript.dependencies || {}).length} dependencies
                      {context.dependencies.javascript.devDependencies && 
                        `, ${Object.keys(context.dependencies.javascript.devDependencies).length} dev dependencies`
                      }
                    </div>
                  </div>
                )}
                
                {context.dependencies.python && context.dependencies.python.dependencies && (
                  <div className="dep-group">
                    <h4>Python</h4>
                    <div className="dep-count">
                      {context.dependencies.python.dependencies.length} packages
                    </div>
                    <div className="dep-list">
                      {context.dependencies.python.dependencies.slice(0, 10).map((dep, idx) => (
                        <div key={idx} className="dep-item">
                          {dep.name} {dep.version !== 'latest' && `(${dep.version})`}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </section>
            )}
          </div>
        )}

        <div className="context-footer">
          <button className="refresh-btn" onClick={loadContext}>
            🔄 Refresh Context
          </button>
        </div>
      </div>
    </>
  );
};

// Helper functions
const getFileIcon = (ext) => {
  const icons = {
    '.js': '📜', '.jsx': '⚛️', '.ts': '🔷', '.tsx': '⚛️',
    '.py': '🐍', '.java': '☕', '.cpp': '⚙️', '.c': '⚙️',
    '.html': '🌐', '.css': '🎨', '.json': '📋', '.md': '📝',
    '.txt': '📄', '.xml': '📋', '.yml': '⚙️', '.yaml': '⚙️'
  };
  return icons[ext] || '📄';
};

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 10) / 10 + ' ' + sizes[i];
};

export default ContextPanel;
