import React, { useState } from 'react';
import { codeExecutionService } from '../../services/codeExecution';
import './CodeRunner.css';

const CodeRunner = ({ code, language }) => {
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);
  const [showOutput, setShowOutput] = useState(false);

  const handleRun = async () => {
    setIsRunning(true);
    setError(null);
    setOutput('');
    setShowOutput(true);

    try {
      await codeExecutionService.execute(code, language, (chunk) => {
        setOutput(prev => prev + chunk + '\n');
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  if (!['python', 'py', 'javascript', 'js'].includes(language.toLowerCase())) {
    return null;
  }

  return (
    <div className="code-runner">
      <div className="runner-header">
        <span className="runner-title">
          {language === 'python' || language === 'py' ? '🐍 Python Sandbox' : '⚡ JS Sandbox'}
        </span>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {isRunning && <span className="runner-status">Running...</span>}
          <button 
            className="run-btn" 
            onClick={handleRun} 
            disabled={isRunning}
          >
            {isRunning ? 'Running...' : '▶ Run Code'}
          </button>
        </div>
      </div>
      
      {showOutput && (
        <div className="runner-output">
          <span className="output-label">Output:</span>
          {error ? (
            <div className="output-content error">{error}</div>
          ) : (
            <div className="output-content">{output || <span style={{color: '#666'}}>(No output)</span>}</div>
          )}
        </div>
      )}
    </div>
  );
};

export default CodeRunner;
