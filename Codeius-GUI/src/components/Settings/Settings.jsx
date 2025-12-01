import React, { useState, useEffect } from 'react';
import { getModels, switchModel } from '../../services/api';
import './Settings.css';

const Settings = ({ onModelChange, currentModel }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [models, setModels] = useState({});
  const [activeModel, setActiveModel] = useState(currentModel || '');
  const [isLoading, setIsLoading] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);

  // Fetch models from backend
  useEffect(() => {
    const fetchModels = async () => {
      setIsLoading(true);
      try {
        const modelData = await getModels();
        setModels(modelData);
      } catch (error) {
        console.error('Failed to fetch models:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (isOpen) {
      fetchModels();
    }
  }, [isOpen]);

  const toggleSettings = () => {
    setIsOpen(!isOpen);
  };

  const handleModelSelect = async (modelKey) => {
    if (modelKey === activeModel) {
      setIsOpen(false);
      return;
    }

    setIsSwitching(true);
    try {
      await switchModel(modelKey);
      setActiveModel(modelKey);
      onModelChange(modelKey);
      setIsOpen(false);
    } catch (error) {
      console.error('Failed to switch model:', error);
      alert('Failed to switch model. Please try again.');
    } finally {
      setIsSwitching(false);
    }
  };

  return (
    <div className="settings-container">
      <button className="settings-btn" onClick={toggleSettings} title="Settings">
        <span className="settings-icon">⚙️</span>
      </button>

      {isOpen && (
        <div className="settings-dropdown">
          <div className="settings-header">
            <h3>⚙️ Settings</h3>
            <button className="settings-close" onClick={toggleSettings}>×</button>
          </div>
          
          <div className="settings-content">
            <div className="model-section">
              <h4>AI Model Selection</h4>
              
              {isLoading ? (
                <div className="loading-models">Loading models...</div>
              ) : (
                <div className="model-list">
                  {Object.entries(models).map(([key, model]) => (
                    <div 
                      key={key} 
                      className={`model-option ${activeModel === key ? 'selected' : ''} ${isSwitching ? 'disabled' : ''}`}
                      onClick={() => !isSwitching && handleModelSelect(key)}
                    >
                      <div className="model-info">
                        <span className="model-name">{model.name}</span>
                        <span className="model-provider">{model.provider}</span>
                      </div>
                      <div className="model-status">
                        {activeModel === key && <span className="current">✓ Active</span>}
                      </div>
                    </div>
                  ))}
                  {Object.keys(models).length === 0 && !isLoading && (
                    <div className="no-models">No models available</div>
                  )}
                </div>
              )}
            </div>

            <div className="privacy-section">
              <h4>💾 Data Privacy</h4>
              <div className="setting-item">
                <span>Remember chat history</span>
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
              <div className="setting-item">
                <span>Auto-save conversations</span>
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {isOpen && <div className="settings-backdrop" onClick={toggleSettings}></div>}
    </div>
  );
};

export default Settings;