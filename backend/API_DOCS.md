# Customer 360 API Documentation

Base URL: `/api/v1`

**Global Authentication Note:** 
All endpoints under `/agents`, `/customers`, `/policies`, and `/llm` are protected and require a valid JWT token. You must pass it via the HTTP headers:
`Authorization: Bearer <your_access_token>`

---

## 1. Authentication

### Login Agent
- **URL**: `/auth/login`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "email": "agent@example.com",
    "password": "your_password"
  }
  ```
- **Expected Response (Success - 200 OK)**:
  ```json
  {
    "agent_data": {
      "id": "uuid-string",
      "name": "Agent Name",
      "email": "agent@example.com",
      "phone_number": "1234567890",
      "agency_name": "Agency LLC",
      "license_number": "LIC123",
      "profile_image_url": "http://localhost:8000/api/v1/auth/images/filename.jpg"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
  ```
- **Expected Response (Error - 401 Unauthorized)**:
  ```json
  {
    "message": "Invalid email or password. Please double-check your credentials and try again."
  }
  ```

### Verify Token
- **URL**: `/auth/verify`
- **Method**: `GET`
- **Headers**:
  - `Authorization: Bearer <token>`
- **Expected Response (Success - 200 OK)**:
  ```json
  {
    "id": "uuid-string",
    "name": "Agent Name",
    "email": "agent@example.com",
    "phone_number": "1234567890",
    "agency_name": "Agency LLC",
    "license_number": "LIC123",
    "profile_image_url": "http://localhost:8000/api/v1/auth/images/filename.jpg"
  }
  ```
- **Expected Response (Error - 401 Unauthorized)**:
  ```json
  {
    "detail": "Invalid or expired token"
  }
  ```

### Get Profile Image
- **URL**: `/auth/images/{filename}`
- **Method**: `GET`
- **Path Params**:
  - `filename` (string): The name of the image file.
- **Expected Response (Success - 200 OK)**: File stream of the image.
- **Expected Response (Failure - 200 OK with Error)**:
  ```json
  {
    "error": "Image not found"
  }
  ```

---

## 2. Agents

### Get Agent Info
- **URL**: `/agents/{insurance_agent_id}`
- **Method**: `GET`
- **Path Params**:
  - `insurance_agent_id` (string): The ID of the agent.
- **Expected Response (Success - 200 OK)**:
  ```json
  {
    "id": "uuid-string",
    "name": "Agent Name",
    "email": "agent@example.com",
    "phone_number": "1234567890",
    "agency_name": "Agency LLC",
    "license_number": "LIC123",
    "profile_image_url": "http://localhost:8000/api/v1/auth/images/filename.jpg"
  }
  ```
- **Expected Response (Error - 404 Not Found)**:
  ```json
  {
    "message": "Agent not found"
  }
  ```

### Get Agent Suggestions
- **URL**: `/agents/{insurance_agent_id}/suggestions`
- **Method**: `GET`
- **Path Params**:
  - `insurance_agent_id` (string): The ID of the agent.
- **Expected Response (Success - 200 OK, Found Cached)**:
  ```json
  {
    "status": "success",
    "message": "Found recent suggestions.",
    "action_text": "1. Call John Doe about his expiring auto policy...\n2. Check in on Jane Doe's life insurance application...",
    "last_updated": "2026-10-02T12:00:00"
  }
  ```
- **Expected Response (Success - 200 OK, Pending Generation)**:
  ```json
  {
    "status": "pending",
    "message": "Analyzing your recent interactions and policies to generate your personalized suggestions for today. This will just take a moment.",
    "job_id": "suggestion-uuid-string"
  }
  ```
---

## 3. Customers

### Get Agent's Customers
- **URL**: `/customers/`
- **Method**: `GET`
- **Query Params**:
  - `insurance_agent_id` (string, required): ID of the agent.
  - `search_term` (string, optional): Search term for name, email, phone, or ID. Results are ordered by best match.
  - `policy_status` (string, optional): Filter by policy status.
  - `policy_type` (string, optional): Filter by policy type.
  - `customer_name` (string, optional): Partial match for customer name.
  - `page` (int, default=1): Page number.
  - `page_size` (int, default=10): Items per page.
- **Expected Response (Success - 200 OK)**:
  ```json
  {
    "total_items": 100,
    "total_pages": 10,
    "current_page": 1,
    "count": 10,
    "items": [
      {
        "id": "uuid-string",
        "name": "Customer Name",
        "email": "customer@example.com",
        "phone_number": "1234567890",
        "date_of_birth": "1990-01-01",
        "address": "123 Main St"
      }
    ]
  }
  ```
- **Expected Response (Error - 422 Unprocessable Entity)** (e.g., missing `insurance_agent_id`):
  ```json
  {
    "detail": [
      {
        "loc": ["query", "insurance_agent_id"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

---

## 4. Policies

### Get Agent's Policies
- **URL**: `/policies/`
- **Method**: `GET`
- **Query Params**:
  - `insurance_agent_id` (string, required): ID of the agent.
  - `status` (string, optional): Filter by policy status.
  - `policy_type` (string, optional): Filter by policy type.
  - `customer_id` (string, optional): Filter by customer ID.
  - `search_term` (string, optional): Search term for ID, agent ID, customer ID, or policy number. Results ordered by best match.
  - `page` (int, default=1): Page number.
  - `page_size` (int, default=10): Items per page.
- **Expected Response (Success - 200 OK)**:
  ```json
  {
    "total_items": 50,
    "total_pages": 5,
    "current_page": 1,
    "count": 10,
    "items": [
      {
        "id": "uuid-string",
        "policy_number": "POL-12345",
        "customer_id": "uuid-string",
        "agent_id": "uuid-string",
        "policy_type": "Life",
        "status": "Active",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "premium_amount": 1000.50,
        "coverage_amount": 500000.00
      }
    ]
  }
  ```
- **Expected Response (Error - 422 Unprocessable Entity)**:
  (Standard FastAPI validation error if required fields are missing)

---

## 5. LLM Operations

### Generate LLM Response (Submit Job)
- **URL**: `/llm/generate`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "query": "What is the policy status?",
    "customers_id": "uuid-string (optional)",
    "insurance_agents_id": "uuid-string (optional)",
    "policies_id": "uuid-string (optional)",
    "callback_url": "https://yourapp.com/callback (optional)"
  }
  ```
- **Expected Response (Success - 200 OK)**:
  ```json
  {
    "status": "job_submitted",
    "job_id": "generated-uuid-string"
  }
  ```
- **Expected Response (Error - 500 Internal Server Error)**:
  ```json
  {
    "message": "Redis Error: Connection refused"
  }
  ```

### LLM Callback (Webhook)
- **URL**: `/llm/callback`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "job_id": "uuid-string",
    "message": "The policy is currently active.",
    "job_type": "general (or suggestions_generation)",
    "customers_id": "uuid-string (optional)",
    "insurance_agents_id": "uuid-string (optional)",
    "policies_id": "uuid-string (optional)"
  }
  ```
- **Expected Response (Success - 200 OK)**:
  ```json
  {
    "status": "success"
  }
  ```
