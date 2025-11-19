# 🚀 EIP Deployment Quickstart Guide

**Entrepreneurship Intelligence Platform - Complete Setup in 30 Minutes**

---

## 📋 Prerequisites

- **Docker & Docker Compose** (v20.10+)
- **Python 3.8+**
- **Node.js 16+** (for mobile app)
- **8GB RAM minimum** (16GB recommended)
- **API Keys**: OpenAI or Anthropic (at least one)

---

## ⚡ Quick Start (5 Minutes)

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd EIP

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

**Required Environment Variables:**
```bash
# LLM API Keys (at least one required)
OPENAI_API_KEY=sk-...your-openai-key
ANTHROPIC_API_KEY=sk-ant-...your-anthropic-key

# Database Credentials
DATABASE_URL=postgresql://eip_user:eip_password@localhost:5432/eip_db
REDIS_URL=redis://localhost:6379/0
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-secure-password
MONGODB_URI=mongodb://localhost:27017/eip

# Security
SECRET_KEY=your-very-secret-key-change-this-in-production
JWT_SECRET_KEY=another-secret-key-for-jwt-tokens

# App Settings
APP_ENV=development
APP_NAME=EIP
```

### 2. Start Infrastructure Services

```bash
# Start all infrastructure services (PostgreSQL, Redis, Neo4j, MongoDB, Kafka, etc.)
docker-compose up -d

# Wait for services to be healthy (~30 seconds)
docker-compose ps

# Check logs if needed
docker-compose logs -f postgres redis neo4j
```

### 3. Initialize Databases

```bash
# Install Python dependencies
pip install -r requirements.txt

# Initialize PostgreSQL schema
python scripts/init_db.py

# Seed knowledge bases (Neo4j + Vector Store)
python scripts/seed_knowledge_base.py

# Create admin user (optional)
python scripts/create_admin.py
```

### 4. Start Backend API

```bash
# Start FastAPI backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 5. Start Frontend Dashboard

```bash
# In a new terminal
cd frontend
streamlit run app.py --server.port 8501

# Frontend will be available at: http://localhost:8501
```

### 6. Verify System

```bash
# In a new terminal
python scripts/verify_system.py

# This will test all components and show status
```

---

## 🎯 Accessing the Platform

| Component | URL | Description |
|-----------|-----|-------------|
| **Frontend Dashboard** | http://localhost:8501 | Main user interface |
| **Backend API** | http://localhost:8000 | REST API endpoints |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **Neo4j Browser** | http://localhost:7474 | Knowledge graph explorer |
| **Redis Commander** | http://localhost:8081 | Redis data browser |

---

## 🧪 Testing the System

### Test 1: Query an AI Agent via Frontend

1. Open http://localhost:8501
2. Login or register a new account
3. Go to "Chat" page
4. Ask: **"What tax deductions are available for startups in India?"**
5. You should get a detailed AI response from the Tax Agent + Policy Agent

### Test 2: Query via API

```bash
# First, get a token
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "name": "Test User"
  }'

# Login
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "testpass123"
  }' | jq -r '.access_token')

# Query the chat endpoint
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can I optimize my startup budget?",
    "session_id": "test-session-1"
  }' | jq .
```

### Test 3: Document Analysis

```bash
# Upload and analyze a PDF document
curl -X POST "http://localhost:8000/api/v1/analyze/document" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/document.pdf" \
  -F "analysis_type=contract"
```

---

## 📊 System Components Status

After running `python scripts/verify_system.py`, you should see:

```
✓ PASS Python Version >= 3.8
✓ PASS PostgreSQL Connection
✓ PASS Redis Connection
✓ PASS Neo4j Connection
✓ PASS MongoDB Connection
✓ PASS LLM Service Initialization
✓ PASS RAG Service Initialization
✓ PASS GraphRAG Service Initialization
✓ PASS OCR Service Initialization
✓ PASS VLM Service Initialization
✓ PASS PolicyAgent
✓ PASS MarketAgent
✓ PASS FinanceAgent
✓ PASS TaxAgent
✓ PASS DistributionAgent
✓ PASS InvestmentAgent
✓ PASS LegalAgent
✓ PASS NewsAgent
✓ PASS Agent Orchestrator
✓ PASS FastAPI Application
✓ PASS Kafka Producers
✓ PASS Kafka Consumers

Success Rate: 95-100%
✓ SYSTEM VERIFICATION PASSED
```

---

## 🔧 Optional: Start Data Pipeline

### For Real-Time News & Market Data Processing

```bash
# Terminal 1: Start Kafka Consumers
python data_pipeline/kafka/consumers.py

# Terminal 2: Start Kafka Producers (optional - for testing)
python data_pipeline/kafka/producers.py
```

### For Batch Processing & Analytics

```bash
# Start Airflow scheduler
airflow scheduler

# Start Airflow web server
airflow webserver --port 8080

# Access Airflow UI at: http://localhost:8080
```

---

## 📱 Mobile App (Optional)

### Setup React Native App

```bash
cd mobile

# Install dependencies
npm install

# For iOS (Mac only)
npx pod-install ios
npx react-native run-ios

# For Android
npx react-native run-android
```

### Configure Backend URL

Edit `mobile/src/services/api.ts`:
```typescript
const API_BASE_URL = 'http://YOUR_IP:8000/api/v1';
```

---

## 🐳 Production Deployment

### Using Docker Compose (Recommended for Small-Medium Scale)

```bash
# Build all services
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# Scale backend instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Using Kubernetes (Recommended for Large Scale)

```bash
# Create namespace
kubectl create namespace eip

# Apply configurations
kubectl apply -f infrastructure/k8s/configmaps/
kubectl apply -f infrastructure/k8s/secrets/
kubectl apply -f infrastructure/k8s/deployments/
kubectl apply -f infrastructure/k8s/services/
kubectl apply -f infrastructure/k8s/ingress/

# Check status
kubectl get pods -n eip
kubectl get services -n eip

# View logs
kubectl logs -f deployment/eip-backend -n eip
```

### Using Terraform (Infrastructure as Code)

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply configuration
terraform apply

# Outputs will show your endpoints and connection details
```

---

## 🧪 Running Tests

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/agents/test_policy_agent.py -v

# Run with coverage
pytest tests/ --cov=backend --cov=agents --cov-report=html
```

### Integration Tests

```bash
# Run integration tests (requires services running)
pytest tests/integration/ -v
```

### End-to-End Tests

```bash
# Run E2E tests (requires full system running)
pytest tests/e2e/ -v
```

---

## 📈 Monitoring & Observability

### Prometheus Metrics

```bash
# Access metrics endpoint
curl http://localhost:8000/metrics

# Prometheus UI (if enabled)
open http://localhost:9090
```

### Grafana Dashboards

```bash
# Access Grafana
open http://localhost:3000

# Default credentials:
# Username: admin
# Password: admin
```

### Logs

```bash
# Backend logs
docker-compose logs -f backend

# All services logs
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
```

---

## 🔍 Troubleshooting

### Issue: "Connection refused" errors

**Solution:**
```bash
# Check if services are running
docker-compose ps

# Restart services
docker-compose restart

# Check service logs
docker-compose logs postgres redis neo4j
```

### Issue: "API key not found" errors

**Solution:**
```bash
# Verify API keys in .env
grep API_KEY .env

# Test OpenAI connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: "Database migration failed"

**Solution:**
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
python scripts/init_db.py
```

### Issue: "Neo4j authentication failed"

**Solution:**
```bash
# Reset Neo4j password
docker-compose down neo4j
docker-compose up -d neo4j
# Wait 30 seconds, then change password via browser at http://localhost:7474
```

### Issue: "Agent returns empty response"

**Solution:**
```bash
# Check LLM service initialization
python -c "from backend.app.services.llm_service import LLMService; s=LLMService(); print('OK')"

# Verify environment variables
python scripts/verify_system.py
```

---

## 📚 Next Steps

1. **Read Documentation**: Check `/docs` folder for detailed guides
2. **Explore API**: Visit http://localhost:8000/docs for interactive API docs
3. **Customize Agents**: Modify agents in `/agents` to fit your needs
4. **Add Data**: Seed more knowledge with custom documents
5. **Configure Monitoring**: Set up Prometheus alerts and Grafana dashboards
6. **Deploy to Production**: Follow K8s or Docker deployment guides above

---

## 🆘 Getting Help

- **Documentation**: `/docs` folder
- **API Reference**: http://localhost:8000/docs
- **System Verification**: `python scripts/verify_system.py`
- **Health Check**: http://localhost:8000/health

---

## ✅ Verification Checklist

Before going to production, verify:

- [ ] All services start successfully (`docker-compose ps`)
- [ ] System verification passes (`python scripts/verify_system.py`)
- [ ] Can login to frontend (http://localhost:8501)
- [ ] Can query AI agents via chat interface
- [ ] Can upload and analyze documents
- [ ] API endpoints return valid responses
- [ ] Neo4j has seeded data (http://localhost:7474)
- [ ] Tests pass (`pytest tests/ -v`)
- [ ] Environment variables are secure (change default passwords)
- [ ] Backups are configured
- [ ] Monitoring is set up (Prometheus + Grafana)

---

## 🎉 You're Ready!

Your Entrepreneurship Intelligence Platform is now fully operational and ready to empower entrepreneurs with AI-powered decision-making!

**Happy Building! 🚀**
