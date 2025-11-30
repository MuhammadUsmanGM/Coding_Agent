import React, { useState } from 'react';
import './Settings.css';

const Settings = ({ onModelChange, currentModel }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customModelName, setCustomModelName] = useState('');
  const [customModelEndpoint, setCustomModelEndpoint] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  
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

  const handleAddCustomModel = (e) => {
    e.preventDefault();
    
    if (customModelName && customModelEndpoint) {
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
                <form className="add-model-form" onSubmit={handleAddCustomModel}>
                  <input
                    type="text"
                    placeholder="Model name"
                    value={customModelName}
                    onChange={(e) => setCustomModelName(e.target.value)}
                    required
                  />
                  <input
                    type="text"
                    placeholder="Model endpoint/API URL"
                    value={customModelEndpoint}
                    onChange={(e) => setCustomModelEndpoint(e.target.value)}
                    required
                  />
                  <div className="form-actions">
                    <button type="submit" className="save-btn">Add Model</button>
                    <button
                      type="button"
                      className="cancel-btn"
                      onClick={() => setShowAddForm(false)}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      )}

      {isOpen && <div className="settings-backdrop" onClick={toggleSettings}></div>}
    </div>
  );
};

export default Settings;