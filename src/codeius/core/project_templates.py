"""
Project Template Manager for Codeius AI Coding Agent
Provides functions to create various project templates
"""
import os
from pathlib import Path

# Import all the individual template functions
from .fastapi_template import create_fastapi_project
from .flask_template import create_flask_project
from .django_template import create_django_project
from .react_template import create_react_project
from .nodejs_template import create_nodejs_project
from .ai_ml_template import create_ai_ml_project

# Dictionary mapping project types to their creation functions
PROJECT_TYPES = {
    'fastapi': create_fastapi_project,
    'flask': create_flask_project,
    'django': create_django_project,
    'react': create_react_project,
    'nodejs': create_nodejs_project,
    'ai_ml': create_ai_ml_project
}

def create_project(project_type: str, project_name: str):
    """Create a project of the specified type."""
    if project_type not in PROJECT_TYPES:
        raise ValueError(f"Unknown project type: {project_type}. Available types: {list(PROJECT_TYPES.keys())}")

    create_func = PROJECT_TYPES[project_type]
    create_func(project_name)

def list_available_templates():
    """Return a list of available project templates."""
    return list(PROJECT_TYPES.keys())

def get_template_description(project_type: str):
    """Get a description of the specified template."""
    descriptions = {
        'fastapi': 'FastAPI project with REST API, database integration, and async support',
        'flask': 'Flask project with application factory pattern and blueprints',
        'django': 'Django project with models, views and admin interface',
        'react': 'React project with Create React App setup and modern components',
        'nodejs': 'Node.js/Express project with MVC pattern and database integration',
        'ai_ml': 'AI/ML project with data science tools and experiment tracking'
    }

    return descriptions.get(project_type, f'Description for {project_type} not available')