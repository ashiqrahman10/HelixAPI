# API Documentation

This document provides an overview of the API endpoints available in our project.

## Table of Contents

1. [Authentication](#authentication)
2. [Patient Management](#patient-management)
3. [Lab Management](#lab-management)

## Authentication

### POST /auth/login

Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

## Patient Management

### GET /patients

Retrieve a list of all patients.

**Headers:**
- Authorization: Bearer {token}

**Response:**
```json
[
  {
    "id": "1",
    "name": "John Doe",
    "dateOfBirth": "1990-01-01",
    "gender": "male"
  },
  {
    "id": "2",
    "name": "Jane Smith",
    "dateOfBirth": "1985-05-15",
    "gender": "female"
  }
]
```

### GET /patients/:id

Retrieve details of a specific patient.

**Headers:**
- Authorization: Bearer {token}

**Parameters:**
- id: Patient ID

**Response:**
```json
{
  "id": "1",
  "name": "John Doe",
  "dateOfBirth": "1990-01-01",
  "gender": "male",
  "email": "john@example.com",
  "phone": "123-456-7890"
}
```

### POST /patients

Create a new patient record.

**Headers:**
- Authorization: Bearer {token}

**Request Body:**```json
{
  "name": "Alice Johnson",
  "dateOfBirth": "1995-08-20",
  "gender": "female",
  "email": "alice@example.com",
  "phone": "987-654-3210"
}
```

**Response:**
```json
{
  "id": "3",
  "name": "Alice Johnson",
  "dateOfBirth": "1995-08-20",
  "gender": "female",
  "email": "alice@example.com",
  "phone": "987-654-3210"
}
```

### PUT /patients/:id

Update an existing patient record.

**Headers:**
- Authorization: Bearer {token}

**Parameters:**
- id: Patient ID

**Request Body:**```json
{
  "name": "Alice Johnson-Smith",
  "phone": "987-654-3211"
}
```

**Response:**
```json
{
  "id": "3",
  "name": "Alice Johnson-Smith",
  "dateOfBirth": "1995-08-20",
  "gender": "female",
  "email": "alice@example.com",
  "phone": "987-654-3211"
}
```

### DELETE /patients/:id

Delete a patient record.

**Headers:**
- Authorization: Bearer {token}

**Parameters:**
- id: Patient ID

**Response:**
```json
{
  "message": "Patient deleted successfully"
}
```

## Lab Management

### GET /labs

Retrieve a list of all lab tests.

**Headers:**
- Authorization: Bearer {token}

**Response:**
```json
[
  {
    "id": "1",
    "name": "Complete Blood Count",
    "code": "CBC001"
  },
  {
    "id": "2",
    "name": "Lipid Panel",
    "code": "LIP002"
  }
]
```

### GET /labs/:id

Retrieve details of a specific lab test.

**Headers:**
- Authorization: Bearer {token}

**Parameters:**
- id: Lab test ID

**Response:**
```json
{
  "id": "1",
  "name": "Complete Blood Count",
  "code": "CBC001",
  "description": "Measures various components and features of blood",
  "price": 50.00
}
```

### POST /labs

Create a new lab test.

**Headers:**
- Authorization: Bearer {token}

**Request Body:**
```json
{
  "name": "Thyroid Function Test",
  "code": "TFT003",
  "description": "Measures thyroid hormones and TSH levels",
  "price": 75.00
}
```

**Response:**
```json
{
  "id": "3",
  "name": "Thyroid Function Test",
  "code": "TFT003",
  "description": "Measures thyroid hormones and TSH levels",
  "price": 75.00
}
```

### PUT /labs/:id

Update an existing lab test.

**Headers:**
- Authorization: Bearer {token}

**Parameters:**
- id: Lab test ID

**Request Body:**
```json
{
  "price": 80.00,
  "description": "Updated description for thyroid function test"
}
```

**Response:**
```json
{
  "id": "3",
  "name": "Thyroid Function Test",
  "code": "TFT003",
  "description": "Updated description for thyroid function test",
  "price": 80.00
}
```

### DELETE /labs/:id

Delete a lab test.

**Headers:**
- Authorization: Bearer {token}

**Parameters:**
- id: Lab test ID

**Response:**
```json
{
  "message": "Lab test deleted successfully"
}
```

## Error Responses

All endpoints may return the following error responses:

- 400 Bad Request: Invalid input data
- 401 Unauthorized: Missing or invalid authentication token
- 403 Forbidden: Insufficient permissions to perform the action
- 404 Not Found: Requested resource not found
- 500 Internal Server Error: Unexpected server error

Error response body:
```json
{
  "error": "Error message describing the issue"
}
```

## Authentication

All endpoints except for `/auth/login` require a valid JWT token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Environment Variables

The following environment variables are required for the API to function properly:

- `PORT`: The port number on which the API server will run
- `DATABASE_URL`: The connection string for the database
- `JWT_SECRET`: The secret key used for JWT token generation and verification

Refer to the `.env.example` file for a template of the required environment variables.

## Getting Started

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables by copying `.env.example` to `.env` and filling in the required values
4. Start the development server: `npm run dev`

For production deployment, use `npm start` to run the compiled version of the application.

## API Versioning

There is currently no API versioning in place. All endpoints are accessed directly without a version prefix.

Example: `http://localhost:3000/patients`

For any questions or issues, please contact our support team.

