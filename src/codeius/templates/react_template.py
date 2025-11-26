"""
React Project Template
This template creates a basic React application structure with:
- Create React App setup
- Component structure
- API integration
- State management
- Folder organization
"""
import os
from pathlib import Path

def create_react_project(project_name: str):
    """Create a basic React project structure."""
    project_path = Path(project_name)
    
    # Create project directories
    (project_path / "public").mkdir(parents=True, exist_ok=True)
    (project_path / "src").mkdir(parents=True, exist_ok=True)
    (project_path / "src" / "components").mkdir(parents=True, exist_ok=True)
    (project_path / "src" / "pages").mkdir(parents=True, exist_ok=True)
    (project_path / "src" / "hooks").mkdir(parents=True, exist_ok=True)
    (project_path / "src" / "utils").mkdir(parents=True, exist_ok=True)
    (project_path / "src" / "services").mkdir(parents=True, exist_ok=True)
    (project_path / "src" / "assets").mkdir(parents=True, exist_ok=True)
    (project_path / "src" / "styles").mkdir(parents=True, exist_ok=True)
    
    # Create public/index.html
    with open(project_path / "public" / "index.html", "w") as f:
        f.write(f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Web site created using Codeius AI React template"
    />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
''')
    
    # Create src/index.js
    with open(project_path / "src" / "index.js", "w") as f:
        f.write('''import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
''')
    
    # Create src/index.css
    with open(project_path / "src" / "index.css", "w") as f:
        f.write('''body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
''')
    
    # Create main App component
    with open(project_path / "src" / "App.js", "w") as f:
        f.write(f'''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import About from './pages/About';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
''')
    
    # Create App.css
    with open(project_path / "src" / "App.css", "w") as f:
        f.write('''.App {
  text-align: center;
}

.App-logo {
  height: 40vmin;
  pointer-events: none;
}

@media (prefers-reduced-motion: no-preference) {
  .App-logo {
    animation: App-logo-spin infinite 20s linear;
  }
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.App-link {
  color: #61dafb;
}

@keyframes App-logo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

main {
  padding: 20px;
  flex: 1;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}
''')
    
    # Create Header component
    with open(project_path / "src" / "components" / "Header.js", "w") as f:
        f.write('''import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Header.css';

const Header = () => {
  return (
    <header className="header">
      <nav className="nav">
        <Link to="/" className="nav-brand">{project_name}</Link>
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className="nav-link">Home</Link>
          </li>
          <li className="nav-item">
            <Link to="/about" className="nav-link">About</Link>
          </li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
''')
    
    # Create Header.css
    with open(project_path / "src" / "styles" / "Header.css", "w") as f:
        f.write('''.header {
  background-color: #282c34;
  color: white;
  padding: 1rem 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
  text-decoration: none;
  color: white;
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-left: 2rem;
}

.nav-link {
  text-decoration: none;
  color: white;
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #61dafb;
}
''')
    
    # Create Footer component
    with open(project_path / "src" / "components" / "Footer.js", "w") as f:
        f.write('''import React from 'react';
import '../styles/Footer.css';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>© {new Date().getFullYear()} {project_name}. All rights reserved.</p>
      </div>
    </footer>
  );
};

export default Footer;
''')
    
    # Create Footer.css
    with open(project_path / "src" / "styles" / "Footer.css", "w") as f:
        f.write('''.footer {
  background-color: #282c34;
  color: white;
  text-align: center;
  padding: 2rem 0;
  margin-top: auto;
  width: 100%;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
''')
    
    # Create Home page
    with open(project_path / "src" / "pages" / "Home.js", "w") as f:
        f.write('''import React, { useState, useEffect } from 'react';
import { fetchData } from '../services/apiService';
import '../styles/Home.css';

const Home = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getData = async () => {
      try {
        const result = await fetchData();
        setData(result);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    getData();
  }, []);

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="home">
      <section className="hero">
        <h1>Welcome to {project_name}</h1>
        <p>A React application generated with Codeius AI</p>
      </section>
      
      <section className="content">
        <h2>Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <h3>Modern UI</h3>
            <p>Clean and responsive design</p>
          </div>
          <div className="feature-card">
            <h3>API Integration</h3>
            <p>Pre-configured API service</p>
          </div>
          <div className="feature-card">
            <h3>Component Architecture</h3>
            <p>Well-organized component structure</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
''')
    
    # Create Home.css
    with open(project_path / "src" / "styles" / "Home.css", "w") as f:
        f.write('''.home {
  width: 100%;
}

.hero {
  text-align: center;
  padding: 4rem 0 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 2rem;
  border-radius: 8px;
}

.hero h1 {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.content {
  text-align: center;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.feature-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 1.2rem;
}
''')
    
    # Create About page
    with open(project_path / "src" / "pages" / "About.js", "w") as f:
        f.write('''import React from 'react';

const About = () => {
  return (
    <div className="about">
      <h1>About {project_name}</h1>
      <p>
        This React application was generated with Codeius AI. 
        It provides a modern, scalable foundation for your next React project.
      </p>
      <div className="tech-stack">
        <h2>Technologies Used</h2>
        <ul>
          <li>React</li>
          <li>React Router</li>
          <li>CSS Modules</li>
          <li>ESLint</li>
          <li>Babel</li>
        </ul>
      </div>
    </div>
  );
};

export default About;
''')
    
    # Create API service
    with open(project_path / "src" / "services" / "apiService.js", "w") as f:
        f.write('''const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const fetchData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/data`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('Error fetching data:', error);
    throw error;
  }
};

export const postData = async (data) => {
  try {
    const response = await fetch(`${API_BASE_URL}/data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  } catch (error) {
    console.error('Error posting data:', error);
    throw error;
  }
};
''')
    
    # Create a sample hook
    with open(project_path / "src" / "hooks" / "useApi.js", "w") as f:
        f.write('''import { useState, useEffect } from 'react';
import { fetchData } from '../services/apiService';

const useApi = (url) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDataFromApi = async () => {
      try {
        setLoading(true);
        const result = await fetchData(url);
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDataFromApi();
  }, [url]);

  return { data, loading, error };
};

export default useApi;
''')
    
    # Create package.json
    with open(project_path / "package.json", "w") as f:
        f.write(f'''{{
  "name": "{project_name.lower().replace(' ', '-')}",
  "version": "1.0.50",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "react-router-dom": "^6.8.0"
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }},
  "eslintConfig": {{
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  }},
  "browserslist": {{
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }}
}}
''')
    
    # Create .env file
    with open(project_path / ".env", "w") as f:
        f.write('''REACT_APP_API_URL=http://localhost:8000/api
''')
    
    # Create README.md
    with open(project_path / "README.md", "w") as f:
        f.write(f'''# {project_name}

A React project template generated with Codeius AI.

## Setup

```bash
npm install
npm start
```

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Runs tests in watch mode
- `npm run eject` - Ejects from Create React App

## Folder Structure

- `public/` - Static assets
- `src/` - Source code
  - `components/` - Reusable UI components
  - `pages/` - Page components
  - `hooks/` - Custom React hooks
  - `services/` - API services
  - `utils/` - Utility functions
  - `styles/` - CSS files
  - `assets/` - Images and other assets
''')
    
    # Create .gitignore
    with open(project_path / ".gitignore", "w") as f:
        f.write('''node_modules/
build/
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
''')
    
    print(f"React project '{project_name}' created successfully!")