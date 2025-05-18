# AI Model API Server

A Node.js server for managing and interacting with AI model APIs.

## Features

- User authentication with JWT
- API key authentication for programmatic access
- Model management (admin only)
- Request tracking
- Secure proxying of API requests to AI models

## Setup and Installation

### Prerequisites

- Node.js (v14+)
- MongoDB

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   PORT=5000
   MONGODB_URI=mongodb://localhost:27017/model-api
   JWT_SECRET=your_jwt_secret_here
   JWT_EXPIRE=30d
   ```

### Running the Server

Development mode:
```
npm run dev
```

Production mode:
```
npm start
```

## API Documentation

### Authentication

#### Register User
- **URL**: `/api/auth/register`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "name": "User Name",
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: JWT token and API key

#### Login
- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: JWT token and API key

### Models

#### Get All Models
- **URL**: `/api/models`
- **Method**: `GET`
- **Auth**: Required (JWT or API key)
- **Response**: List of available models

#### Get Single Model
- **URL**: `/api/models/:id`
- **Method**: `GET`
- **Auth**: Required (JWT or API key)
- **Response**: Model details

#### Create Model (Admin only)
- **URL**: `/api/models`
- **Method**: `POST`
- **Auth**: Required (JWT or API key)
- **Body**:
  ```json
  {
    "name": "Model Name",
    "description": "Model description",
    "endpoint": "https://api.example.com/model",
    "parameters": {
      "temperature": 0.7
    },
    "apiKey": "model_api_key",
    "isPublic": true
  }
  ```
- **Response**: Created model

### Model Requests

#### Make a Request to a Model
- **URL**: `/api/models/:id/request`
- **Method**: `POST`
- **Auth**: Required (JWT or API key)
- **Body**: Model-specific parameters
- **Response**: Model output

#### Get User's Request History
- **URL**: `/api/requests`
- **Method**: `GET`
- **Auth**: Required (JWT or API key)
- **Response**: List of user's requests

#### Get Single Request
- **URL**: `/api/requests/:id`
- **Method**: `GET`
- **Auth**: Required (JWT or API key)
- **Response**: Request details

## Security

- Passwords are hashed using bcrypt
- Authentication is handled with JWT tokens and API keys
- Role-based access control for admin functions
- API keys can be regenerated if compromised

## License

ISC 