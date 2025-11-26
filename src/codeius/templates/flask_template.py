"""
Flask Project Template
This template creates a basic Flask application structure with:
- Application factory pattern
- Blueprints
- Configuration
- Requirements file
- Basic routes
"""
import os
from pathlib import Path

def create_flask_project(project_name: str):
    """Create a basic Flask project structure."""
    project_path = Path(project_name)
    
    # Create project directories
    (project_path / "app").mkdir(parents=True, exist_ok=True)
    (project_path / "app" / "main").mkdir(parents=True, exist_ok=True)
    (project_path / "app" / "auth").mkdir(parents=True, exist_ok=True)
    (project_path / "app" / "models").mkdir(parents=True, exist_ok=True)
    (project_path / "app" / "templates").mkdir(parents=True, exist_ok=True)
    (project_path / "app" / "static").mkdir(parents=True, exist_ok=True)
    (project_path / "app" / "static" / "css").mkdir(parents=True, exist_ok=True)
    (project_path / "app" / "static" / "js").mkdir(parents=True, exist_ok=True)
    (project_path / "app" / "static" / "images").mkdir(parents=True, exist_ok=True)
    (project_path / "tests").mkdir(parents=True, exist_ok=True)
    
    # Create main app file
    with open(project_path / "app" / "__init__.py", "w") as f:
        f.write('''from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

from app import models
''')
    
    # Create main blueprint
    with open(project_path / "app" / "main" / "__init__.py", "w") as f:
        f.write('''from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes
''')
    
    with open(project_path / "app" / "main" / "routes.py", "w") as f:
        f.write('''from flask import render_template, request, jsonify
from app.main import bp
from app.models import User

@bp.route('/')
def index():
    return render_template('index.html', title='Home')

@bp.route('/api/users')
def get_users():
    # This would normally come from the database
    users = [
        {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
        {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'}
    ]
    return jsonify(users)
''')
    
    # Create auth blueprint
    with open(project_path / "app" / "auth" / "__init__.py", "w") as f:
        f.write('''from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes
''')
    
    with open(project_path / "app" / "auth" / "routes.py", "w") as f:
        f.write('''from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.models import User
from app import db

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        
        login_user(user)
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', title='Sign In')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
''')

    # Create models
    with open(project_path / "app" / "models" / "__init__.py", "w") as f:
        f.write('''from app import db, login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
''')
    
    # Create config
    with open(project_path / "config.py", "w") as f:
        f.write('''import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
''')
    
    # Create requirements.txt
    with open(project_path / "requirements.txt", "w") as f:
        f.write('''Flask==3.1.0
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.0.7
Flask-Login==0.6.3
Flask-WTF==1.2.2
WTForms==3.2.1
python-dotenv==1.0.1
email-validator==2.2.0
gunicorn==23.0.0
''')
    
    # Create .env file
    with open(project_path / ".env", "w") as f:
        f.write('''SECRET_KEY=your-secret-key-here
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=sqlite:///app.db
''')
    
    # Create run.py for easy execution
    with open(project_path / "run.py", "w") as f:
        f.write('''from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
''')
    
    # Create README.md
    with open(project_path / "README.md", "w") as f:
        f.write(f'''# {project_name}

A Flask project template generated with Codeius AI.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python run.py
```

## Endpoints

- `GET /` - Home page
- `GET /api/users` - Get users API
- `GET /auth/login` - Login page
- `GET /auth/register` - Registration page
''')
    
    # Create basic templates
    with open(project_path / "app" / "templates" / "base.html", "w") as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% if title %}{{ title }} - {% endif %}Flask App</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-md navbar-dark bg-dark mb-4">
        <div class="container-fluid">
            <a class="navbar-brand" href="{{ url_for('main.index') }}">Flask App</a>
            <div class="navbar-nav ms-auto">
                {% if current_user.is_anonymous %}
                <a class="nav-link" href="{{ url_for('auth.login') }}">Login</a>
                <a class="nav-link" href="{{ url_for('auth.register') }}">Register</a>
                {% else %}
                <span class="navbar-text me-3">Hi, {{ current_user.username }}!</span>
                <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
            <div class="alert alert-info" role="alert">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
''')

    with open(project_path / "app" / "templates" / "index.html", "w") as f:
        f.write('''{% extends "base.html" %}

{% block content %}
<div class="jumbotron">
    <h1 class="display-4">Welcome to Flask App!</h1>
    <p class="lead">This is a basic Flask application generated with Codeius AI.</p>
    <hr class="my-4">
    <p>Get started by exploring the features.</p>
</div>
{% endblock %}
''')

    # Create tests
    with open(project_path / "tests" / "__init__.py", "w") as f:
        f.write('')
        
    with open(project_path / "tests" / "test_app.py", "w") as f:
        f.write('''import unittest
from app import create_app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Flask App!', response.data)

if __name__ == '__main__':
    unittest.main()
''')
    
    print(f"Flask project '{project_name}' created successfully!")