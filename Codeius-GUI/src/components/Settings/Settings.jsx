import React, { useState } from 'react';
import './Settings.css';

const Settings = ({ onModelChange, currentModel }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customModelName, setCustomModelName] = useState('');
  const [customModelEndpoint, setCustomModelEndpoint] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [errors, setErrors] = useState({});
  
  // Default models
  const [models, setModels] = useState([
    { id: 'groq-llama3', name: 'Groq - Llama 3', provider: 'Groq', default: true },
    { id: 'google-gemini', name: 'Google - Gemini', provider: 'Google', default: true }
  ]);

  const toggleSettings = () => {
    setIsOpen(!isOpen);
  };

  const handleModelSelect = (modelId) => {
    onModelChange(modelId);
    setIsOpen(false); // Close the dropdown after selection
  };

  const handleAddCustomModel = () => {
    if (customModelName && customModelEndpoint && apiKey) {
      const newModel = {
        id: `custom-${Date.now()}`, // Unique ID
        name: customModelName,
        provider: 'Custom',
        endpoint: customModelEndpoint,
        default: false
      };

      setModels([...models, newModel]);
      setCustomModelName('');
      setCustomModelEndpoint('');
      setApiKey('');
      setShowAddForm(false);
    }
  };

  return (
    <div className="settings-container">
      <button className="settings-btn" onClick={toggleSettings}>
        <span className="settings-icon">⚙️</span>
      </button>

      {isOpen && (
        <div className="settings-dropdown">
          <div className="settings-header">
            <h3>Settings</h3>
          </div>
          
          <div className="settings-content">
            <div className="model-section">
              <h4>Model Selection</h4>
              
              <div className="model-list">
                {models.map((model) => (
                  <div 
                    key={model.id} 
                    className={`model-option ${currentModel === model.id ? 'selected' : ''}`}
                    onClick={() => handleModelSelect(model.id)}
                  >
                    <div className="model-info">
                      <span className="model-name">{model.name}</span>
                      <span className="model-provider">{model.provider}</span>
                    </div>
                    <div className="model-status">
                      {currentModel === model.id && <span className="current">Current</span>}
                    </div>
                  </div>
                ))}
              </div>
              
              <button 
                className="add-model-btn"
                onClick={() => setShowAddForm(!showAddForm)}
              >
                + Add Custom Model
              </button>
              
              {showAddForm && (
                <form
                  className="add-model-form"
                  onSubmit={(e) => {
                    e.preventDefault();

                    // Custom validation
                    const newErrors = {};

                    if (!customModelName.trim()) {
                      newErrors.customModelName = "Please enter a model name";
                    }

                    if (!customModelEndpoint.trim()) {
                      newErrors.customModelEndpoint = "Please enter a model endpoint/API URL";
                    }

                    if (!apiKey.trim()) {
                      newErrors.apiKey = "Please enter an API key";
                    }

                    setErrors(newErrors);

                    // Only proceed if there are no errors
                    if (Object.keys(newErrors).length === 0) {
                      handleAddCustomModel();
                    }
                  }}
                >
                  <input
                    type={`text ${errors.customModelName ? 'error' : ''}`}
                    placeholder="Model name"
                    value={customModelName}
                    onChange={(e) => {
                      setCustomModelName(e.target.value);
                      if (errors.customModelName) {
                        setErrors(prev => ({...prev, customModelName: ''}));
                      }
                    }}
                  />
                  {errors.customModelName && <div className="error-message">{errors.customModelName}</div>}

                  <input
                    type={`text ${errors.customModelEndpoint ? 'error' : ''}`}
                    placeholder="Model endpoint/API URL"
                    value={customModelEndpoint}
                    onChange={(e) => {
                      setCustomModelEndpoint(e.target.value);
                      if (errors.customModelEndpoint) {
                        setErrors(prev => ({...prev, customModelEndpoint: ''}));
                      }
                    }}
                  />
                  {errors.customModelEndpoint && <div className="error-message">{errors.customModelEndpoint}</div>}

                  <input
                    type={`password ${errors.apiKey ? 'error' : ''}`}
                    placeholder="API key for custom model"
                    value={apiKey}
                    onChange={(e) => {
                      setApiKey(e.target.value);
                      if (errors.apiKey) {
                        setErrors(prev => ({...prev, apiKey: ''}));
                      }
                    }}
                  />
                  {errors.apiKey && <div className="error-message">{errors.apiKey}</div>}
                  <div className="form-actions">
                    <button type="submit" className="save-btn">Add Model</button>
                    <button
                      type="button"
                      className="cancel-btn"
                      onClick={() => {
                        setShowAddForm(false);
                        // Reset form fields when cancelled
                        setCustomModelName('');
                        setCustomModelEndpoint('');
                        setApiKey('');
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>

            <div className="notification-section">
              <h4>Notification Settings</h4>
              <div className="setting-item">
                <span>Enable notifications</span>
                <label className="switch">
                  <input type="checkbox" />
                  <span className="slider"></span>
                </label>
              </div>
              <div className="setting-item">
                <span>Model change alerts</span>
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
            </div>

            <div className="privacy-section">
              <h4>Data Privacy</h4>
              <div className="setting-item">
                <span>Share usage data</span>
                <label className="switch">
                  <input type="checkbox" />
                  <span className="slider"></span>
                </label>
              </div>
              <div className="setting-item">
                <span>Remember chat history</span>
                <label className="switch">
                  <input type="checkbox" defaultChecked />
                  <span className="slider"></span>
                </label>
              </div>
            </div>

            <div className="advanced-section">
              <h4>Advanced Model Config</h4>
              <div className="setting-item">
                <span>Temperature</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  defaultValue="0.7"
                  className="slider-input"
                />
              </div>
              <div className="setting-item">
                <span>Max Tokens</span>
                <select className="config-selector">
                  <option value="1024">1024</option>
                  <option value="2048" selected>2048</option>
                  <option value="4096">4096</option>
                  <option value="8192">8192</option>
                </select>
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