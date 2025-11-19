# 🚀 ENTREPRENEURSHIP INTELLIGENCE PLATFORM (EIP)
## Complete BUILD, RUN & DEPLOYMENT GUIDE

**Last Updated:** November 19, 2025
**Project Status:** ✅ 100% COMPLETE - 35 AI Agents Fully Integrated
**Version:** 1.0.0

---

## 📋 TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Local Development - Quick Start](#local-development)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Production Checklist](#production-checklist)

---

## 🎯 SYSTEM OVERVIEW

### What You're Building

The EIP is a comprehensive AI-powered decision-making platform with:

- **35 Specialized AI Agents** (8 Core + 27 Enhanced)
- **Multi-Agent Orchestration** with A2A (Agent-to-Agent) communication
- **Real-time Intelligence Dashboard** (Streamlit)
- **RESTful API Backend** (FastAPI)
- **Knowledge Systems** (GraphRAG with Neo4j, Vector Store, Redis Memory)
- **Data Pipeline** (Kafka, Spark, Airflow)

### Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│ FRONTEND: Streamlit Dashboard                          │
├─────────────────────────────────────────────────────────┤
│ API GATEWAY: FastAPI (35 Agents Integrated)            │
├─────────────────────────────────────────────────────────┤
│ AGENT SYSTEM: Enhanced Orchestrator + 35 Agents        │
├─────────────────────────────────────────────────────────┤
│ INTELLIGENCE: LLM, VLM, OCR, GraphRAG, RAG              │
├─────────────────────────────────────────────────────────┤
│ DATA: PostgreSQL, MongoDB, Neo4j, Redis, Vector Store   │
├─────────────────────────────────────────────────────────┤
│ PIPELINE: Kafka, Spark, Airflow                         │
├─────────────────────────────────────────────────────────┤
│ INFRA: Docker, Kubernetes, Prometheus, Grafana          │
└─────────────────────────────────────────────────────────┘
```

---

## 🔧 PREREQUISITES

### Required Software

| Component | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.11+ | Backend & AI agents |
| **Node.js** | 18+ | Mobile app (optional) |
| **Docker** | 24+ | Containerization |
| **Docker Compose** | 2.20+ | Local multi-service setup |
| **Kubernetes** | 1.28+ | Production orchestration |
| **Git** | 2.40+ | Version control |

### Required API Keys

```bash
# LLM Providers (at least ONE required)
OPENAI_API_KEY=sk-...           # For GPT-4, GPT-4V
ANTHROPIC_API_KEY=sk-ant-...    # For Claude
DEEPSEEK_API_KEY=...            # For DeepSeek-R1 (optional)

# Vector Store (ONE required)
PINECONE_API_KEY=...            # For Pinecone
PINECONE_ENVIRONMENT=...
# OR
CHROMA_PATH=./data/chroma       # For local Chroma

# Optional Services
AWS_ACCESS_KEY_ID=...           # For AWS Textract OCR
AWS_SECRET_ACCESS_KEY=...
NEWS_API_KEY=...                # For news aggregation
ALPHA_VANTAGE_API_KEY=...       # For stock market data
```

### System Requirements

**Development:**
- CPU: 4+ cores
- RAM: 8GB minimum, 16GB recommended
- Disk: 20GB free space

**Production:**
- CPU: 8+ cores
- RAM: 32GB minimum
- Disk: 100GB+ SSD
- Network: 100Mbps+

---

## 🛠️ ENVIRONMENT SETUP

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/EIP.git
cd EIP
```

### Step 2: Create Environment File

```bash
cp .env.example .env
```

### Step 3: Configure .env File

Edit `.env` with your actual values:

```bash
# ============================================
# CRITICAL: LLM API KEYS (MUST CONFIGURE)
# ============================================
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here

# ============================================
# DATABASE CONFIGURATION
# ============================================
# PostgreSQL (OLTP)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eip_db
POSTGRES_USER=eip_user
POSTGRES_PASSWORD=your_secure_password_here

# MongoDB (Unstructured Data)
MONGODB_URI=mongodb://localhost:27017/eip

# Neo4j (GraphRAG)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# Redis (Memory & Cache)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password_here

# ============================================
# VECTOR STORE (Choose ONE)
# ============================================
# Option 1: Pinecone (Cloud)
PINECONE_API_KEY=your-pinecone-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX=eip-knowledge

# Option 2: Chroma (Local)
CHROMA_PATH=./data/chroma
VECTOR_STORE=chroma  # or 'pinecone'

# ============================================
# KAFKA & DATA PIPELINE
# ============================================
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPICS=news_stream,market_stream,policy_stream

# ============================================
# OPTIONAL API KEYS
# ============================================
NEWS_API_KEY=your-news-api-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# ============================================
# APPLICATION SETTINGS
# ============================================
ENVIRONMENT=development  # or 'production'
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
```

---

## 🚀 LOCAL DEVELOPMENT

### Method 1: Quick Start (Recommended for Testing)

**1. Install Python Dependencies**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

**2. Start Core Services with Docker Compose**

```bash
# Start databases and supporting services
docker-compose up -d postgres mongodb neo4j redis kafka

# Wait for services to be ready (30-60 seconds)
docker-compose ps
```

**3. Initialize Databases**

```bash
# Initialize PostgreSQL schema
python scripts/init_db.py

# Seed knowledge base (optional but recommended)
python scripts/seed_knowledge_base.py
```

**4. Start Backend API**

```bash
# Navigate to backend directory
cd backend

# Run FastAPI server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Backend Running:** http://localhost:8000
✅ **API Docs:** http://localhost:8000/docs
✅ **Health Check:** http://localhost:8000/health

**5. Start Frontend Dashboard (New Terminal)**

```bash
# Navigate to frontend directory
cd frontend

# Run Streamlit dashboard
streamlit run app.py --server.port 8501
```

✅ **Dashboard Running:** http://localhost:8501

**6. Test the System**

Open browser → http://localhost:8501 → Login → Ask a question:

```
Example Queries:
- "What government subsidies are available for my tech startup in India?"
- "Analyze the real estate market in Mumbai for commercial investment"
- "Should I invest in AAPL and MSFT stocks?"
- "Recommend a business model for a SaaS HR platform"
```

---

### Method 2: Full Docker Stack

**1. Build All Images**

```bash
# Build all Docker images
docker-compose build

# Or build specific services
docker-compose build backend frontend
```

**2. Start All Services**

```bash
# Start entire stack (15+ services)
docker-compose up -d

# View logs
docker-compose logs -f backend frontend

# Check service status
docker-compose ps
```

**3. Verify Services**

```bash
# Check all services are healthy
docker-compose ps

# Expected services:
# - postgres (PostgreSQL database)
# - mongodb (MongoDB database)
# - neo4j (Graph database)
# - redis (In-memory cache)
# - kafka (Message broker)
# - zookeeper (Kafka coordinator)
# - backend (FastAPI server)
# - frontend (Streamlit dashboard)
# - prometheus (Monitoring)
# - grafana (Visualization)
```

**4. Access Services**

| Service | URL | Default Credentials |
|---------|-----|---------------------|
| Frontend Dashboard | http://localhost:8501 | Register new account |
| Backend API Docs | http://localhost:8000/docs | N/A (JWT required) |
| PostgreSQL | localhost:5432 | See .env |
| MongoDB | localhost:27017 | See .env |
| Neo4j Browser | http://localhost:7474 | neo4j / password from .env |
| Redis | localhost:6379 | See .env |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | N/A |

---

## ☸️ KUBERNETES DEPLOYMENT (Production)

### Prerequisites

- Kubernetes cluster (EKS, GKE, AKS, or local minikube)
- `kubectl` configured
- Docker images pushed to container registry

### Step 1: Configure Container Registry

```bash
# Build and tag images
docker build -t your-registry.com/eip-backend:1.0.0 -f docker/Dockerfile.backend .
docker build -t your-registry.com/eip-frontend:1.0.0 -f docker/Dockerfile.frontend .

# Push to registry
docker push your-registry.com/eip-backend:1.0.0
docker push your-registry.com/eip-frontend:1.0.0
```

### Step 2: Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace eip-prod

# Create secrets from .env
kubectl create secret generic eip-secrets \
  --from-literal=OPENAI_API_KEY=$OPENAI_API_KEY \
  --from-literal=POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
  --from-literal=NEO4J_PASSWORD=$NEO4J_PASSWORD \
  --from-literal=REDIS_PASSWORD=$REDIS_PASSWORD \
  --from-literal=SECRET_KEY=$SECRET_KEY \
  -n eip-prod

# Create database credentials
kubectl create secret generic db-credentials \
  --from-literal=postgres-password=$POSTGRES_PASSWORD \
  --from-literal=mongodb-password=$MONGODB_PASSWORD \
  --from-literal=neo4j-password=$NEO4J_PASSWORD \
  --from-literal=redis-password=$REDIS_PASSWORD \
  -n eip-prod
```

### Step 3: Deploy Infrastructure Services

```bash
# Deploy databases and supporting services
kubectl apply -f infrastructure/k8s/databases/ -n eip-prod

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n eip-prod --timeout=300s
kubectl wait --for=condition=ready pod -l app=mongodb -n eip-prod --timeout=300s
kubectl wait --for=condition=ready pod -l app=neo4j -n eip-prod --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n eip-prod --timeout=300s
```

### Step 4: Deploy Application

```bash
# Deploy backend API
kubectl apply -f infrastructure/k8s/backend/ -n eip-prod

# Deploy frontend dashboard
kubectl apply -f infrastructure/k8s/frontend/ -n eip-prod

# Deploy ingress
kubectl apply -f infrastructure/k8s/ingress/ -n eip-prod
```

### Step 5: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n eip-prod

# Check services
kubectl get svc -n eip-prod

# Check ingress
kubectl get ingress -n eip-prod

# View logs
kubectl logs -f deployment/backend -n eip-prod
kubectl logs -f deployment/frontend -n eip-prod
```

### Step 6: Access Application

```bash
# Get ingress IP/hostname
kubectl get ingress -n eip-prod

# Application will be available at configured domain
# Example: https://eip.yourdomain.com
```

### Step 7: Enable Monitoring

```bash
# Deploy Prometheus & Grafana
kubectl apply -f infrastructure/k8s/monitoring/ -n eip-prod

# Access Grafana (port-forward for testing)
kubectl port-forward svc/grafana 3000:3000 -n eip-prod

# Open: http://localhost:3000 (admin / admin)
```

---

## 🧪 TESTING

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=backend --cov-report=html

# Test specific component
pytest tests/unit/test_agents.py -v
```

### Integration Tests

```bash
# Ensure services are running
docker-compose up -d

# Run integration tests
pytest tests/integration/ -v
```

### End-to-End Tests

```bash
# Run E2E user journey tests
pytest tests/e2e/test_user_journeys.py -v

# Test all 35 agents
python scripts/test_all_agents.py
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

---

## 🔍 TROUBLESHOOTING

### Issue 1: "Module not found" errors

```bash
# Solution: Ensure all dependencies installed
pip install -r requirements.txt

# If specific package missing
pip install <package-name>
```

### Issue 2: Database connection errors

```bash
# Check if database is running
docker-compose ps postgres

# View database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Verify connection
docker-compose exec postgres psql -U eip_user -d eip_db -c "SELECT 1"
```

### Issue 3: "API Key not found" errors

```bash
# Verify .env file exists
cat .env | grep OPENAI_API_KEY

# Ensure environment variables are loaded
# In Python:
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### Issue 4: Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue 5: Out of memory errors

```bash
# Increase Docker memory
# Docker Desktop → Settings → Resources → Memory → 8GB+

# Or reduce agent count (edit orchestrator)
# Comment out some agents in enhanced_agent_orchestrator.py
```

### Issue 6: Slow agent responses

```bash
# Possible causes:
1. Missing vector store data → Run: python scripts/seed_knowledge_base.py
2. Network latency to LLM APIs → Check internet connection
3. Insufficient resources → Increase RAM allocation
4. Cold start → First request is always slower

# Enable debug logging
LOG_LEVEL=DEBUG in .env
```

---

## ✅ PRODUCTION CHECKLIST

### Security

- [ ] Change all default passwords in `.env`
- [ ] Use strong `SECRET_KEY` for JWT
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Configure CORS properly in FastAPI
- [ ] Enable rate limiting on API endpoints
- [ ] Set up firewall rules
- [ ] Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
- [ ] Enable database encryption at rest

### Performance

- [ ] Configure Horizontal Pod Autoscaling (HPA) in K8s
- [ ] Set up CDN for frontend assets
- [ ] Enable Redis caching for frequent queries
- [ ] Configure database connection pooling
- [ ] Implement request/response compression
- [ ] Set up load balancer
- [ ] Optimize Docker images (multi-stage builds)

### Monitoring

- [ ] Deploy Prometheus for metrics
- [ ] Set up Grafana dashboards
- [ ] Configure alerting (PagerDuty, Slack)
- [ ] Enable application performance monitoring (APM)
- [ ] Set up log aggregation (ELK stack)
- [ ] Configure uptime monitoring
- [ ] Track LLM token usage and costs

### Backup & Recovery

- [ ] Set up automated database backups
- [ ] Configure backup retention policy
- [ ] Test restore procedures
- [ ] Implement disaster recovery plan
- [ ] Set up cross-region replication (if applicable)

### Compliance

- [ ] Review data privacy policies (GDPR, CCPA)
- [ ] Implement audit logging
- [ ] Set up data retention policies
- [ ] Configure user consent management
- [ ] Review third-party API terms of service

---

## 📊 SERVICE ARCHITECTURE

### Core Services

```yaml
# Service Dependencies
Frontend (Streamlit)
  ↓
Backend API (FastAPI)
  ↓
Agent Orchestrator (35 Agents)
  ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   LLM       │   GraphRAG  │   Vector    │   Memory    │
│ (GPT-4, etc)│   (Neo4j)   │   Store     │   (Redis)   │
└─────────────┴─────────────┴─────────────┴─────────────┘
  ↓             ↓             ↓             ↓
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ PostgreSQL  │  MongoDB    │   Kafka     │   Spark     │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

### Data Flow

```
User Query
  ↓
Frontend (Streamlit) → API Gateway (FastAPI)
  ↓
Enhanced Orchestrator (Query Classification)
  ↓
Primary Agent + Secondary Agents (Parallel Execution)
  ↓
RAG Retrieval + GraphRAG + LLM Generation
  ↓
Response Synthesis
  ↓
Return to User + Store in DB + Cache in Redis
```

---

## 📝 NEXT STEPS

After successful deployment:

1. **Seed Knowledge Base**: Run `python scripts/seed_knowledge_base.py`
2. **Create Admin User**: Run `python scripts/create_admin.py`
3. **Configure Airflow DAGs**: Set up data ingestion pipelines
4. **Enable Monitoring**: Access Grafana dashboards
5. **Test All Agents**: Run `python scripts/test_all_agents.py`
6. **Review Documentation**: See `/docs` for detailed API specs

---

## 🆘 SUPPORT

- **GitHub Issues**: https://github.com/yourusername/EIP/issues
- **Documentation**: `/docs` directory
- **Email**: support@eip-platform.com

---

## 🎉 SUCCESS INDICATORS

Your deployment is successful when:

✅ All 35 agents respond correctly
✅ Dashboard loads without errors
✅ API health check returns 200
✅ Database connections established
✅ Grafana shows green metrics
✅ Test queries return AI-generated responses
✅ No critical errors in logs

**Congratulations! Your EIP is now fully operational with 35 specialized AI agents! 🚀**
