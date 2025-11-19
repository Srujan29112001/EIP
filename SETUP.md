# EIP Setup Guide

## Quick Start (Development)

### Prerequisites
- Docker Desktop installed
- Python 3.11+
- Git

### Option 1: Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd EIP
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Start all services with Docker Compose**
```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- MongoDB (port 27017)
- Redis (port 6379)
- Neo4j (ports 7474, 7687)
- Kafka (ports 9092, 29092)
- Backend API (port 8000)
- Frontend Dashboard (port 8501)
- Prometheus (port 9090)
- Grafana (port 3001)

4. **Initialize database**
```bash
docker-compose exec backend python scripts/init_db.py
docker-compose exec backend python scripts/create_admin.py
```

5. **Access the application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474
- Grafana: http://localhost:3001 (admin/admin)

6. **Login credentials**
- Email: admin@eip.com
- Password: admin123

### Option 2: Local Development

1. **Install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Start databases (Docker)**
```bash
# Start only database services
docker-compose up -d postgres mongodb redis neo4j kafka zookeeper
```

3. **Set up environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

4. **Initialize database**
```bash
python scripts/init_db.py
python scripts/create_admin.py
```

5. **Start backend**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Start frontend (in new terminal)**
```bash
cd frontend
streamlit run app.py
```

## Configuration

### Required API Keys

Add these to your `.env` file:

```env
# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=...  # Optional

# External Data APIs
NEWS_API_KEY=...
ALPHA_VANTAGE_API_KEY=...

# Security
SECRET_KEY=<generate-random-32-char-string>
JWT_SECRET_KEY=<generate-random-32-char-string>
```

### Generate Secret Keys
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Testing the System

### 1. Test Backend API
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","environment":"development","timestamp":...}
```

### 2. Test User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "password123",
    "tier": "aspiring"
  }'
```

### 3. Test Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 4. Test Chat (with token)
```bash
TOKEN="<your-access-token>"

curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the tax benefits for startups in India?"
  }'
```

## Database Management

### View PostgreSQL Data
```bash
docker-compose exec postgres psql -U eip_user -d eip_db

# Inside psql:
\dt  # List tables
SELECT * FROM users;
\q   # Quit
```

### View MongoDB Data
```bash
docker-compose exec mongodb mongosh mongodb://admin:admin_password@localhost:27017

# Inside mongosh:
use eip_documents
show collections
db.documents.find()
exit
```

### View Redis Data
```bash
docker-compose exec redis redis-cli

# Inside redis-cli:
KEYS *
GET session:*
exit
```

### View Neo4j Data
- Open http://localhost:7474
- Username: neo4j
- Password: neo4j_password

## Monitoring

### Prometheus
- URL: http://localhost:9090
- Check targets: http://localhost:9090/targets

### Grafana
- URL: http://localhost:3001
- Username: admin
- Password: admin

## Troubleshooting

### Services not starting
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Restart specific service
docker-compose restart backend
```

### Database connection errors
```bash
# Ensure databases are healthy
docker-compose ps

# Restart databases
docker-compose restart postgres mongodb redis neo4j
```

### Port already in use
```bash
# Find process using port
lsof -i :8000  # On Mac/Linux
netstat -ano | findstr :8000  # On Windows

# Kill process or change port in .env
```

### Clear all data and restart
```bash
# Stop and remove all containers, networks, volumes
docker-compose down -v

# Restart
docker-compose up -d
```

## Development Workflow

### 1. Making Changes

Backend changes:
- Edit files in `backend/app/`
- FastAPI will auto-reload

Frontend changes:
- Edit files in `frontend/`
- Streamlit will auto-reload

Agent changes:
- Edit files in `agents/`
- Restart backend: `docker-compose restart backend`

### 2. Adding New Dependencies
```bash
# Add to requirements.txt
echo "new-package==1.0.0" >> requirements.txt

# Rebuild containers
docker-compose build backend frontend
docker-compose up -d
```

### 3. Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Production Deployment

See `docs/DEPLOYMENT.md` for production deployment guide with Kubernetes.

## Getting Help

- Documentation: `docs/`
- API Documentation: http://localhost:8000/docs
- Issues: GitHub Issues
- Support: support@eip-platform.com
