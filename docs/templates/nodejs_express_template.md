# Node.js/Express Project Template

## Overview
The Node.js/Express Project Template creates a full-featured Express.js application with MongoDB integration following the MVC pattern. It includes user authentication, security features, and a well-organized folder structure.

## Features
- Express.js web framework
- MongoDB integration with Mongoose ODM
- JWT-based authentication system
- MVC architectural pattern
- Security middleware (Helmet, CORS, rate limiting)
- Environment configuration
- User registration and login endpoints
- RESTful API design
- Testing framework with Jest and Supertest

## Generated Structure
```
project_name/
├── src/                    # Source code
│   ├── server.js          # Main server file
│   ├── config/            # Configuration files
│   │   └── database.js
│   ├── controllers/       # Request handlers
│   │   └── userController.js
│   ├── models/            # Database models
│   │   └── User.js
│   ├── routes/            # API routes
│   │   └── userRoutes.js
│   ├── middleware/        # Custom middleware
│   │   ├── errorHandler.js
│   │   └── auth.js
│   └── utils/             # Utility functions
├── tests/                  # Test files
│   ├── __init__.py
│   └── user.test.js
├── package.json           # Node.js dependencies and scripts
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

## Setup and Usage
1. Generate the project using Codeius AI
2. Install dependencies: `npm install`
3. Set up environment variables in `.env`
4. Start the development server: `npm run dev` (with nodemon) or `npm start`

## Key Components

### Main Server (`src/server.js`)
- Express app initialization
- Security middleware setup
- Body parsing middleware
- Database connection
- Route definitions
- Error handling middleware

### Database Configuration (`src/config/database.js`)
- MongoDB connection setup
- Connection error handling
- Connection status logging

### Models (`src/models/User.js`)
- Mongoose schema definition
- Password hashing with bcrypt
- Password comparison method
- Validation rules

### Controllers (`src/controllers/userController.js`)
- Request handling logic
- User registration and login
- Token generation with JWT
- Input validation

### Routes (`src/routes/userRoutes.js`)
- API endpoint definitions
- Route-specific middleware
- Controller function mapping

### Middleware (`src/middleware/`)
- Authentication middleware
- Error handling middleware
- Security and validation

## API Endpoints
- `GET /` - Health check
- `POST /api/users/register` - Register a new user
- `POST /api/users/login` - Login user
- `GET /api/users/me` - Get current user (requires auth)

## Environment Variables
- `NODE_ENV` - Environment mode (development/production)
- `PORT` - Server port (default: 3000)
- `MONGODB_URI` - MongoDB connection string
- `JWT_SECRET` - Secret for JWT token signing
- `JWT_EXPIRE` - JWT token expiration time

## Extending the Template
1. Add new models in the models directory
2. Create additional controllers for new functionality
3. Define new routes in the routes directory
4. Implement validation with Joi or other libraries
5. Add more middleware for specific requirements
6. Create service layers for complex business logic

## Best Practices
- Use async/await for asynchronous operations
- Implement proper error handling
- Validate input data using appropriate libraries
- Use environment variables for configuration
- Follow RESTful API design principles
- Implement proper authentication and authorization
- Use middleware for cross-cutting concerns

## Security Features
- Password hashing with bcrypt
- JWT-based authentication
- Helmet.js security headers
- CORS configuration
- Rate limiting to prevent abuse
- Input validation and sanitization
- Protection against common vulnerabilities (XSS, CSRF)