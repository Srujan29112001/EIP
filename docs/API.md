# EIP API Documentation

## Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://api.eip-platform.com/api/v1`

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123",
  "tier": "aspiring"  // Options: aspiring, mid, top
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "tier": "aspiring",
  "created_at": "2024-01-15T10:30:00",
  "is_active": true,
  "is_verified": false,
  "metadata": {}
}
```

#### Login
```http
POST /auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe",
  "tier": "aspiring",
  "created_at": "2024-01-15T10:30:00",
  "is_active": true,
  "is_verified": false,
  "metadata": {}
}
```

### Chat / Query

#### Send Query
```http
POST /chat/
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "query": "What are the tax benefits for startups in India?",
  "session_id": "optional-uuid",
  "context": {},
  "agent_preference": "tax"  // Optional
}
```

**Response:**
```json
{
  "query_id": "uuid",
  "session_id": "uuid",
  "answer": "Detailed response about tax benefits...",
  "agent_used": "tax",
  "sources": [
    {
      "title": "Section 80IAC - Startup Exemption",
      "content": "Eligible startups can claim...",
      "url": "https://example.com",
      "relevance_score": 0.95
    }
  ],
  "confidence_score": 0.9,
  "latency_ms": 1234.56,
  "tokens_used": 500,
  "timestamp": "2024-01-15T10:30:00"
}
```

#### Get Chat History
```http
GET /chat/history/{session_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "session_id": "uuid",
  "messages": [
    "user: What are tax benefits?",
    "assistant: Here are the tax benefits..."
  ]
}
```

#### Clear Chat History
```http
DELETE /chat/history/{session_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Chat history cleared successfully"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Account is inactive"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "message": "An error occurred"
}
```

## Rate Limiting

- **Default**: 100 requests per minute per user
- **Headers Returned**:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

## Pagination

For endpoints returning lists:

```http
GET /endpoint?limit=20&offset=0
```

**Parameters:**
- `limit`: Number of items per page (max: 100)
- `offset`: Number of items to skip

## Webhooks (Planned)

Subscribe to events:
- `query.completed`
- `document.processed`
- `alert.triggered`

## SDK Examples

### Python
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "password123"}
)
token = response.json()["access_token"]

# Query
response = requests.post(
    "http://localhost:8000/api/v1/chat/",
    headers={"Authorization": f"Bearer {token}"},
    json={"query": "Market size for EV in India?"}
)
answer = response.json()["answer"]
print(answer)
```

### JavaScript
```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});
const { access_token } = await loginResponse.json();

// Query
const queryResponse = await fetch('http://localhost:8000/api/v1/chat/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    query: 'Market size for EV in India?'
  })
});
const data = await queryResponse.json();
console.log(data.answer);
```

## Interactive Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation where you can test all endpoints directly.
