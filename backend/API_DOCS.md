# Customer 360 API Documentation

Base URL: `/api/v1`

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
    "message": "Invalid email or password. Please double-check your credentials and try again."
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

---

## 3. Customers

### Get Agent's Customers
- **URL**: `/customers/`
- **Method**: `GET`
- **Query Params**:
  - `insurance_agent_id` (string, required): ID of the agent.
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
