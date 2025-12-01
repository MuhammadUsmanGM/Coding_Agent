import React, { useState } from 'react';
import { useToast } from '../Toast/ToastContainer';
import {
  getGitStatus,
  gitAdd,
  gitCommit,
  gitPush,
  gitPull,
  gitClone,
  gitBranch,
  gitLog
} from '../../services/git';
import './GitControls.css';

const GitControls = () => {
  const [showGitMenu, setShowGitMenu] = useState(false);
  const [showCommitModal, setShowCommitModal] = useState(false);
  const [showOperationModal, setShowOperationModal] = useState(false);
  const [modalType, setModalType] = useState(''); // 'clone', 'create-branch', 'switch-branch'
  const [commitMessage, setCommitMessage] = useState('');
  const [operationInputs, setOperationInputs] = useState({
    url: '',
    destination: '',
    branchName: ''
  });
  const [repoStatus, setRepoStatus] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState(false);
  const toast = useToast();

  const handleGitOperation = async (operation, data = {}) => {
    try {
      let result;
      
      switch (operation) {
        case 'add':
          result = await gitAdd(data.files);
          break;
        case 'commit':
          result = await gitCommit(data.message);
          break;
        case 'push':
          result = await gitPush(data.remote, data.branch);
          break;
        case 'pull':
          result = await gitPull(data.remote, data.branch);
          break;
        case 'clone':
          result = await gitClone(data.url, data.destination);
          break;
        case 'branch':
          if (data.create) {
            result = await gitBranch(data.create);
          } else if (data.switch) {
            result = await gitBranch(null, data.switch);
          } else {
            toast.error('No branch action specified');
            return;
          }
          break;
        case 'log':
          result = await gitLog(data.limit || 10);
          break;
        case 'status':
        default:
          result = await getGitStatus();
          break;
      }
      
      if (result.success) {
        toast.success(`Git ${operation} completed successfully`);
        if (operation === 'commit') {
          // Refresh status after commit
          fetchRepoStatus();
        }
      } else {
        toast.error(`Git ${operation} failed: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      toast.error(`Error performing git ${operation}: ${error.message}`);
    }
  };

  const fetchRepoStatus = async () => {
    setLoadingStatus(true);
    try {
      const result = await getGitStatus();
      if (result.success) {
        setRepoStatus(result.output || 'Clean');
      } else {
        setRepoStatus(`Error: ${result.error || 'Could not get status'}`);
        toast.error(`Git status error: ${result.error || 'Could not get status'}`);
      }
    } catch (error) {
      setRepoStatus(`Error: ${error.message}`);
      toast.error(`Git status error: ${error.message}`);
    } finally {
      setLoadingStatus(false);
    }
  };

  const handleStatusClick = async () => {
    await fetchRepoStatus();
  };

  const handleCommitSubmit = () => {
    if (commitMessage.trim()) {
      handleGitOperation('commit', { message: commitMessage });
      setCommitMessage(''); // Clear the input
      setShowCommitModal(false); // Close the modal
    } else {
      toast.warning('Please enter a commit message');
    }
  };

  const handleCommitCancel = () => {
    setCommitMessage('');
    setShowCommitModal(false);
  };

  const handleOperationSubmit = () => {
    switch (modalType) {
      case 'clone':
        if (operationInputs.url.trim()) {
          handleGitOperation('clone', { 
            url: operationInputs.url,
            destination: operationInputs.destination.trim() || undefined
          });
          setOperationInputs({ url: '', destination: '', branchName: '' });
          setShowOperationModal(false);
        } else {
          toast.warning('Please enter a repository URL');
        }
        break;
      case 'create-branch':
        if (operationInputs.branchName.trim()) {
          handleGitOperation('branch', { create: operationInputs.branchName });
          setOperationInputs(prev => ({ ...prev, branchName: '' }));
          setShowOperationModal(false);
        } else {
          toast.warning('Please enter a branch name');
        }
        break;
      case 'switch-branch':
        if (operationInputs.branchName.trim()) {
          handleGitOperation('branch', { switch: operationInputs.branchName });
          setOperationInputs(prev => ({ ...prev, branchName: '' }));
          setShowOperationModal(false);
        } else {
          toast.warning('Please enter a branch name');
        }
        break;
      default:
        break;
    }
  };

  const handleOperationCancel = () => {
    setOperationInputs({
      url: '',
      destination: '',
      branchName: ''
    });
    setShowOperationModal(false);
  };

  const handleInputChange = (field, value) => {
    setOperationInputs(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="git-controls">
      <div className="git-status-indicator" onClick={handleStatusClick}>
        <span className="git-icon">📊</span>
        <span className="git-status-text">
          {loadingStatus ? 'Checking...' : repoStatus || 'Check Status'}
        </span>
      </div>

      <div className="git-btn-group">
        <button className="git-btn git-add-btn" onClick={() => handleGitOperation('add', { files: '.' })}>
          <span className="git-btn-icon">➕</span>
          <span className="git-btn-label">Add</span>
        </button>

        <button className="git-btn git-commit-btn" onClick={() => {
          setShowCommitModal(true);
        }}>
          <span className="git-btn-icon">📝</span>
          <span className="git-btn-label">Commit</span>
        </button>

        <button className="git-btn git-push-btn" onClick={() => handleGitOperation('push')}>
          <span className="git-btn-icon">📤</span>
          <span className="git-btn-label">Push</span>
        </button>

        <button className="git-btn git-pull-btn" onClick={() => handleGitOperation('pull')}>
          <span className="git-btn-icon">📥</span>
          <span className="git-btn-label">Pull</span>
        </button>

        <div className="git-menu-toggle">
          <button
            className="git-more-btn"
            onClick={() => setShowGitMenu(!showGitMenu)}
          >
            <span className="git-btn-icon">⋯</span>
            <span className="git-btn-label">More</span>
          </button>

          {showGitMenu && (
            <div className="git-dropdown-menu">
              <button onClick={() => handleGitOperation('status')}>Status</button>
              <button onClick={() => handleGitOperation('log', { limit: 10 })}>Log</button>
              <button onClick={() => {
                setModalType('clone');
                setShowOperationModal(true);
              }}>Clone</button>
              <button onClick={() => {
                setModalType('create-branch');
                setShowOperationModal(true);
              }}>Create Branch</button>
              <button onClick={() => {
                setModalType('switch-branch');
                setShowOperationModal(true);
              }}>Switch Branch</button>
            </div>
          )}
        </div>
      </div>

      {/* Commit Message Modal */}
      {showCommitModal && (
        <div className="modal-overlay" onClick={handleCommitCancel}>
          <div className="commit-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Commit Changes</h3>
              <button className="close-btn" onClick={handleCommitCancel}>×</button>
            </div>
            <div className="modal-body">
              <label htmlFor="commit-message">Commit Message:</label>
              <textarea
                id="commit-message"
                className="commit-message-input"
                placeholder="Enter your commit message..."
                value={commitMessage}
                onChange={(e) => setCommitMessage(e.target.value)}
                rows="4"
              />
            </div>
            <div className="modal-footer">
              <button className="cancel-btn" onClick={handleCommitCancel}>Cancel</button>
              <button className="commit-submit-btn" onClick={handleCommitSubmit}>Commit</button>
            </div>
          </div>
        </div>
      )}

      {/* Operation Modal (Clone, Branch Operations) */}
      {showOperationModal && (
        <div className="modal-overlay" onClick={handleOperationCancel}>
          <div className="commit-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>
                {modalType === 'clone' && 'Clone Repository'}
                {modalType === 'create-branch' && 'Create Branch'}
                {modalType === 'switch-branch' && 'Switch Branch'}
              </h3>
              <button className="close-btn" onClick={handleOperationCancel}>×</button>
            </div>
            <div className="modal-body">
              {modalType === 'clone' && (
                <>
                  <label htmlFor="repo-url">Repository URL:</label>
                  <input
                    type="text"
                    id="repo-url"
                    className="operation-input"
                    placeholder="https://github.com/username/repository.git"
                    value={operationInputs.url}
                    onChange={(e) => handleInputChange('url', e.target.value)}
                  />
                  <label htmlFor="destination" style={{marginTop: '10px'}}>Destination (optional):</label>
                  <input
                    type="text"
                    id="destination"
                    className="operation-input"
                    placeholder="Leave blank for current directory"
                    value={operationInputs.destination}
                    onChange={(e) => handleInputChange('destination', e.target.value)}
                  />
                </>
              )}
              {(modalType === 'create-branch' || modalType === 'switch-branch') && (
                <>
                  <label htmlFor="branch-name">
                    {modalType === 'create-branch' ? 'New Branch Name:' : 'Branch Name to Switch To:'}
                  </label>
                  <input
                    type="text"
                    id="branch-name"
                    className="operation-input"
                    placeholder="Enter branch name"
                    value={operationInputs.branchName}
                    onChange={(e) => handleInputChange('branchName', e.target.value)}
                  />
                </>
              )}
            </div>
            <div className="modal-footer">
              <button className="cancel-btn" onClick={handleOperationCancel}>Cancel</button>
              <button className="commit-submit-btn" onClick={handleOperationSubmit}>
                {modalType === 'clone' && 'Clone'}
                {modalType === 'create-branch' && 'Create'}
                {modalType === 'switch-branch' && 'Switch'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GitControls;