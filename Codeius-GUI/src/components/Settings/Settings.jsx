import React, { useState, useEffect } from 'react';
import { getModels, switchModel } from '../../services/api';
import { useToast } from '../Toast/ToastContainer';
import LoadingSpinner from '../LoadingSpinner/LoadingSpinner';
import './Settings.css';

const Settings = ({ onModelChange, currentModel }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [customModelName, setCustomModelName] = useState('');
  const [customModelEndpoint, setCustomModelEndpoint] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [errors, setErrors] = useState({});
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCustomInstructionsModal, setShowCustomInstructionsModal] = useState(false);
  const [customInstructions, setCustomInstructions] = useState(`You are an expert coding assistant. Follow these guidelines:
- Provide clear, concise code solutions
- Explain complex concepts in simple terms
- Use best practices for the requested language
- Consider performance implications
- Suggest improvements when appropriate`);
  const toast = useToast();

  useEffect(() => {
    if (isOpen) {
      loadModels();
    }
  }, [isOpen]);

  const loadModels = async () => {
    try {
      setLoading(true);
      const modelList = await getModels();

      // If the API returns models, use those
      if (modelList && Object.keys(modelList).length > 0) {
        const formattedModels = Object.entries(modelList).map(([key, model]) => ({
          id: key,
          name: model.name,
          provider: model.provider,
          description: model.description
        }));
        setModels(formattedModels);
      } else {
        // Fallback to default models if API returns empty
        const defaultModels = [
          { id: 'groq-llama3', name: 'Groq - Llama 3', provider: 'Groq' },
          { id: 'google-gemini', name: 'Google - Gemini', provider: 'Google' }
        ];
        setModels(defaultModels);
      }
    } catch (error) {
      // On error, show default models
      const defaultModels = [
        { id: 'groq-llama3', name: 'Groq - Llama 3', provider: 'Groq' },
        { id: 'google-gemini', name: 'Google - Gemini', provider: 'Google' }
      ];
      setModels(defaultModels);
      toast.error('Failed to load models from server, showing defaults: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleSettings = () => {
    setIsOpen(!isOpen);
  };

  const handleModelSelect = async (modelId) => {
    try {
      const result = await switchModel(modelId);
      toast.success(result); // Show the result message from backend
      setIsOpen(false); // Close the dropdown after selection
      onModelChange(modelId);
    } catch (error) {
      toast.error('Failed to switch model: ' + error.message);
    }
  };

  const handleAddCustomModel = () => {
    if (customModelName && customModelEndpoint && apiKey) {
      // In the current implementation, custom models are managed by the backend
      // This form is just for UI demonstration - in a real implementation,
      // you would call an API endpoint to add custom models
      toast.info('Custom model configuration would be sent to backend in a full implementation');

      // Reset form
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

              {loading ? (
                <LoadingSpinner size="small" message="Loading models..." />
              ) : (
                <div className="model-list">
                  {models.length > 0 ? (
                    models.map((model) => (
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
                    ))
                  ) : (
                    <div className="loading-models">No models available</div>
                  )}
                </div>
              )}

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
                  <input type="checkbox" defaultChecked />
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

            <div className="custom-instructions-section">
              <h4>Custom AI Instructions</h4>
              <button className="edit-instructions-btn" onClick={() => setShowCustomInstructionsModal(true)}>
                Edit Custom Instructions
              </button>
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

      {/* Custom Instructions Modal */}
      {showCustomInstructionsModal && (
        <div className="custom-instructions-modal">
          <div className="custom-instructions-content">
            <div className="custom-instructions-header">
              <h3>Custom AI Instructions</h3>
              <button
                className="close-modal-btn"
                onClick={() => setShowCustomInstructionsModal(false)}
              >
                &times;
              </button>
            </div>

            <div className="custom-instructions-body">
              <div className="instructions-presets">
                <h4>Predefined Templates</h4>
                <div className="preset-options">
                  <button
                    className="preset-btn"
                    onClick={() => setCustomInstructions(`You are an expert Frontend Developer. Focus on:
- HTML, CSS, JavaScript, React, Vue, or Angular
- Modern UI/UX implementation
- Responsive design principles
- Browser compatibility
- Performance optimization for frontend assets`)}
                  >
                    Frontend Development
                  </button>
                  <button
                    className="preset-btn"
                    onClick={() => setCustomInstructions(`You are an expert Backend Developer. Focus on:
- Server-side logic, databases, APIs
- Security best practices
- Scalability and performance
- Integration patterns
- Architecture design`)}
                  >
                    Backend Development
                  </button>
                  <button
                    className="preset-btn"
                    onClick={() => setCustomInstructions(`You are an expert Data Analyst. Focus on:
- Statistical analysis
- Data visualization
- Data cleaning and preprocessing
- Python or R for analysis
- Interpretation of results`)}
                  >
                    Data Analysis
                  </button>
                  <button
                    className="preset-btn"
                    onClick={() => setCustomInstructions(`You are an expert DevOps Engineer. Focus on:
- CI/CD pipelines
- Infrastructure as Code
- Containerization (Docker, Kubernetes)
- Monitoring and observability
- Cloud platforms and deployment`)}
                  >
                    DevOps
                  </button>
                </div>
              </div>

              <div className="instructions-editor">
                <label htmlFor="custom-instructions">Custom Instructions</label>
                <textarea
                  id="custom-instructions"
                  className="instructions-textarea"
                  placeholder="Enter your custom instructions for the AI assistant..."
                  rows="8"
                  value={customInstructions}
                  onChange={(e) => setCustomInstructions(e.target.value)}
                ></textarea>
              </div>

              <div className="instructions-actions">
                <button
                  className="save-instructions-btn"
                  onClick={() => {
                    toast.success('Custom instructions saved successfully!');
                    setShowCustomInstructionsModal(false);
                  }}
                >
                  Save Instructions
                </button>
                <button
                  className="cancel-instructions-btn"
                  onClick={() => setShowCustomInstructionsModal(false)}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Settings;