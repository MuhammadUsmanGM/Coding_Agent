"""
FastAPI Project Template
This template creates a basic FastAPI application structure with:
- Main application file
- Router modules
- Configuration
- Requirements file
- Basic endpoints
"""
import os
from pathlib import Path

def create_fastapi_project(project_name: str):
    """Create a basic FastAPI project structure."""
    project_path = Path(project_name)
    
    # Create project directories
    (project_path / "api").mkdir(parents=True, exist_ok=True)
    (project_path / "config").mkdir(parents=True, exist_ok=True)
    (project_path / "models").mkdir(parents=True, exist_ok=True)
    (project_path / "schemas").mkdir(parents=True, exist_ok=True)
    (project_path / "database").mkdir(parents=True, exist_ok=True)
    (project_path / "utils").mkdir(parents=True, exist_ok=True)
    (project_path / "tests").mkdir(parents=True, exist_ok=True)
    
    # Create main app file
    with open(project_path / "main.py", "w") as f:
        f.write('''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router
import uvicorn
from config.settings import settings

app = FastAPI(
    title="FastAPI Project",
    description="A FastAPI project template",
    version="1.0.50",
    openapi_url="/api/v1/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Project!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
''')
    
    # Create API router
    with open(project_path / "api" / "__init__.py", "w") as f:
        f.write('from .router import router\n')

    with open(project_path / "api" / "router.py", "w") as f:
        f.write(f'''from fastapi import APIRouter
from schemas.user import User, UserCreate
from models.user import users_db

router = APIRouter()

@router.get("/users/", response_model=list[User])
def get_users(skip: int = 0, limit: int = 100):
    return list(users_db.values())[skip: skip + limit]

@router.post("/users/", response_model=User)
def create_user(user: UserCreate):
    user_id = len(users_db) + 1
    db_user = User(id=user_id, name=user.name, email=user.email)
    users_db[user_id] = db_user
    return db_user
''')
    
    # Create models
    with open(project_path / "models" / "__init__.py", "w") as f:
        f.write('')
        
    with open(project_path / "models" / "user.py", "w") as f:
        f.write('''# In-memory database for demo purposes
users_db = {}

class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

class UserCreate:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
''')
    
    # Create schemas
    with open(project_path / "schemas" / "__init__.py", "w") as f:
        f.write('')
        
    with open(project_path / "schemas" / "user.py", "w") as f:
        f.write('''from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

class UserCreate(BaseModel):
    name: str
    email: str
''')
    
    # Create config
    with open(project_path / "config" / "__init__.py", "w") as f:
        f.write('')
        
    with open(project_path / "config" / "settings.py", "w") as f:
        f.write('''from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = True
    ALLOWED_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"

settings = Settings()
''')
    
    # Create requirements.txt
    with open(project_path / "requirements.txt", "w") as f:
        f.write('''fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.12.4
pydantic-settings==2.6.1
python-multipart==0.0.20
python-dotenv==1.0.1
SQLAlchemy==2.0.36
alembic==1.14.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
''')
    
    # Create .env file
    with open(project_path / ".env", "w") as f:
        f.write('''HOST=127.0.0.1
PORT=8000
RELOAD=True
''')
    
    # Create README.md
    with open(project_path / "README.md", "w") as f:
        f.write(f'''# {project_name}

A FastAPI project template generated with Codeius AI.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload
```

## Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /api/v1/users/` - Get users
- `POST /api/v1/users/` - Create user
''')

    # Create tests
    with open(project_path / "tests" / "__init__.py", "w") as f:
        f.write('')
        
    with open(project_path / "tests" / "test_main.py", "w") as f:
        f.write('''from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
''')
    
    print(f"FastAPI project '{project_name}' created successfully!")