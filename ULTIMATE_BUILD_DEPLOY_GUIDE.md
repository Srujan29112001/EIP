# 🚀 ULTIMATE BUILD, RUN & DEPLOY GUIDE
## Entrepreneurship Intelligence Platform (EIP)

**Complete Guide to Build, Test, Run and Deploy Your 35-Agent AI Platform**

---

## 📋 TABLE OF CONTENTS

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 Minutes)](#quick-start)
3. [Full Local Development Setup](#local-development)
4. [Testing All Components](#testing)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Production Deployment](#kubernetes-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Configuration Guide](#configuration)

---

## 🎯 PREREQUISITES

### Required Software

```bash
# Check your versions
python --version    # Need: Python 3.11+
node --version      # Need: Node 18+
docker --version    # Need: Docker 20+
kubectl version     # Need: Kubernetes 1.24+ (for production)
```

### System Requirements

**Minimum (Development)**:
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB free

**Recommended (Production)**:
- CPU: 8+ cores
- RAM: 16+ GB
- Disk: 100+ GB

### API Keys (Required for AI Features)

You need AT LEAST ONE of these:

1. **OpenAI** (Recommended)
   - Go to: https://platform.openai.com/api-keys
   - Create API key
   - Cost: ~$0.01 per query

2. **Anthropic Claude** (Alternative)
   - Go to: https://console.anthropic.com/
   - Create API key
   - Cost: ~$0.015 per query

3. **DeepSeek** (Optional, for reasoning)
   - Go to: https://platform.deepseek.com/
   - Create API key
   - Cost: ~$0.005 per query

---

## ⚡ QUICK START (5 Minutes)

### Step 1: Clone & Install Dependencies

```bash
# Clone the repository (if not already done)
cd /home/user/EIP

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all dependencies (this may take 5-10 minutes)
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or vim .env, or use any text editor
```

**Minimum Required in .env**:
```env
# Required: At least one LLM provider
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database URLs (default for local development)
DATABASE_URL=postgresql://eip:eip123@localhost:5432/eip_db
MONGODB_URL=mongodb://localhost:27017/eip
NEO4J_URL=bolt://localhost:7687
REDIS_URL=redis://localhost:6379/0

# App settings
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-change-this-in-production
```

### Step 3: Start Services with Docker Compose

```bash
# Start all infrastructure services
# (PostgreSQL, MongoDB, Neo4j, Redis, Kafka)
docker-compose up -d

# Wait for services to be ready (30 seconds)
sleep 30

# Initialize databases
python scripts/init_db.py
```

### Step 4: Test the System

```bash
# Run comprehensive test suite
python scripts/run_comprehensive_tests.py
```

**Expected Output**: All 35 agents should pass ✅

### Step 5: Start the Application

**Terminal 1 - Backend API**:
```bash
# Start FastAPI backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend Dashboard**:
```bash
# Start Streamlit frontend
streamlit run frontend/app.py --server.port 8501
```

### Step 6: Access the Platform

- **Frontend Dashboard**: http://localhost:8501
- **Backend API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

🎉 **You're Running!** Test by asking a query in the dashboard.

---

## 🛠️ FULL LOCAL DEVELOPMENT SETUP

### Detailed Installation Steps

#### 1. Set Up Python Environment

```bash
# Ensure you have Python 3.11+
python --version

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
pip list | grep streamlit
pip list | grep langchain
```

#### 2. Set Up Infrastructure Services

**Option A: Using Docker Compose (Recommended)**

```bash
# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f
```

**Option B: Install Locally**

<details>
<summary>Click to expand local installation instructions</summary>

**PostgreSQL**:
```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian
sudo apt-get install postgresql-15
sudo systemctl start postgresql

# Create database
createdb eip_db
createuser -P eip  # Password: eip123
```

**MongoDB**:
```bash
# macOS
brew install mongodb-community
brew services start mongodb-community

# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongod
```

**Redis**:
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis
```

**Neo4j**:
```bash
# Download from: https://neo4j.com/download/
# Or use Docker:
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  neo4j:latest
```

**Kafka** (Optional for real-time features):
```bash
# Download from: https://kafka.apache.org/downloads
# Or use Docker (included in docker-compose.yml)
```

</details>

#### 3. Initialize Databases

```bash
# Create database tables
python scripts/init_db.py

# Run migrations (if needed)
cd backend
alembic upgrade head

# Verify database connection
python -c "from backend.app.models.database import engine; print('DB Connected:', engine.connect())"
```

#### 4. Verify All Components

```bash
# Test all 35 agents
python scripts/run_comprehensive_tests.py

# Test backend services
python -c "from backend.app.services.llm_service import LLMService; print('LLM Service OK')"

# Test orchestrator
python -c "from agents.orchestrator.enhanced_agent_orchestrator import EnhancedAgentOrchestrator; o = EnhancedAgentOrchestrator(); print(f'Orchestrator OK: {len(o.agents)} agents')"
```

---

## 🧪 TESTING ALL COMPONENTS

### Test Suite 1: Agent Tests

```bash
# Test all 35 agents
python scripts/run_comprehensive_tests.py

# Test specific agent
python -c "
from agents.enhanced.stock_analysis_agent import StockAnalysisAgent
agent = StockAnalysisAgent()
print('StockAnalysisAgent: OK')
"

# Quick test (3 sample agents)
python scripts/run_comprehensive_tests.py --quick
```

### Test Suite 2: Backend API Tests

```bash
# Start backend
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &

# Wait for startup
sleep 5

# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint (requires auth token)
# First, get auth token:
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

# Then test chat:
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What are the tax benefits for startups in India?"}'
```

### Test Suite 3: Integration Tests

```bash
# Run integration tests
cd tests
pytest integration/ -v

# Test end-to-end workflow
pytest integration/test_e2e_workflow.py -v
```

### Test Suite 4: Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load/locustfile.py --host=http://localhost:8000
```

---

## 🐳 DOCKER DEPLOYMENT

### Build Docker Images

```bash
# Build backend image
docker build -t eip-backend:latest -f docker/Dockerfile.backend .

# Build frontend image
docker build -t eip-frontend:latest -f docker/Dockerfile.frontend .

# Verify images
docker images | grep eip
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Clean up volumes
docker-compose down -v
```

### Access Deployed Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## ☸️ KUBERNETES PRODUCTION DEPLOYMENT

### Prerequisites

```bash
# Install kubectl
# macOS: brew install kubectl
# Ubuntu: sudo apt-get install kubectl

# Install helm (optional)
# macOS: brew install helm
# Ubuntu: curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Configure kubectl to your cluster
# AWS EKS:
aws eks update-kubeconfig --name eip-cluster --region us-east-1

# GCP GKE:
gcloud container clusters get-credentials eip-cluster --zone us-central1-a
```

### Step 1: Set Up Infrastructure with Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan

# Apply (create AWS infrastructure)
terraform apply -auto-approve

# This creates:
# - EKS cluster
# - RDS PostgreSQL database
# - ElastiCache Redis
# - DocumentDB (MongoDB)
# - S3 buckets
# - VPC, subnets, security groups
```

### Step 2: Configure Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace eip-production

# Create secrets
kubectl create secret generic eip-secrets \
  --from-literal=OPENAI_API_KEY=your-key \
  --from-literal=ANTHROPIC_API_KEY=your-key \
  --from-literal=DATABASE_URL=postgresql://... \
  --from-literal=SECRET_KEY=your-secret \
  -n eip-production

# Verify secrets
kubectl get secrets -n eip-production
```

### Step 3: Deploy to Kubernetes

```bash
cd infrastructure/k8s

# Apply ConfigMaps
kubectl apply -f configmaps/ -n eip-production

# Deploy databases (if not using managed services)
kubectl apply -f databases/ -n eip-production

# Deploy backend
kubectl apply -f deployments/backend-deployment.yaml -n eip-production
kubectl apply -f services/backend-service.yaml -n eip-production

# Deploy frontend
kubectl apply -f deployments/frontend-deployment.yaml -n eip-production
kubectl apply -f services/frontend-service.yaml -n eip-production

# Deploy ingress
kubectl apply -f ingress/ -n eip-production

# Deploy monitoring
kubectl apply -f monitoring/ -n eip-production
```

### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods -n eip-production

# Check services
kubectl get svc -n eip-production

# Check ingress
kubectl get ingress -n eip-production

# View logs
kubectl logs -f deployment/backend -n eip-production
kubectl logs -f deployment/frontend -n eip-production
```

### Step 5: Set Up Monitoring

```bash
# Install Prometheus & Grafana
kubectl apply -f infrastructure/k8s/monitoring/prometheus.yaml
kubectl apply -f infrastructure/k8s/monitoring/grafana.yaml

# Access Grafana
kubectl port-forward svc/grafana 3000:3000 -n eip-production

# Login: admin / admin (change password)
# Import dashboards from infrastructure/monitoring/dashboards/
```

### Step 6: Set Up Auto-Scaling

```bash
# Apply Horizontal Pod Autoscaler
kubectl apply -f infrastructure/k8s/hpa/ -n eip-production

# Verify HPA
kubectl get hpa -n eip-production

# Test scaling
# Generate load and watch pods scale
kubectl get pods -n eip-production -w
```

---

## 🔧 CONFIGURATION GUIDE

### Environment Variables Reference

```env
# ========================================
# CORE APPLICATION SETTINGS
# ========================================
APP_NAME=EIP
APP_ENV=production  # development, staging, production
DEBUG=false
SECRET_KEY=your-super-secret-key-change-this
API_HOST=0.0.0.0
API_PORT=8000

# ========================================
# LLM PROVIDERS (Need at least ONE)
# ========================================
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7

ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-4
ANTHROPIC_TEMPERATURE=0.7

DEEPSEEK_API_KEY=sk-...
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.7

# ========================================
# DATABASES
# ========================================
# PostgreSQL (OLTP)
DATABASE_URL=postgresql://user:pass@localhost:5432/eip_db
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# MongoDB (Unstructured)
MONGODB_URL=mongodb://localhost:27017/eip
MONGODB_DB_NAME=eip

# Neo4j (GraphRAG)
NEO4J_URL=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123

# Redis (Cache & Memory)
REDIS_URL=redis://localhost:6379/0
REDIS_POOL_SIZE=10

# ========================================
# VECTOR STORES
# ========================================
# Chroma (Local)
CHROMA_PERSIST_DIR=./data/chroma

# Pinecone (Cloud)
PINECONE_API_KEY=your-key
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=eip-index

# ========================================
# DATA PIPELINE
# ========================================
# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_NEWS=news_stream
KAFKA_TOPIC_MARKET=market_stream
KAFKA_TOPIC_POLICY=policy_stream

# Spark
SPARK_MASTER=local[*]
SPARK_APP_NAME=EIP-Analytics

# Airflow
AIRFLOW_HOME=./data_pipeline/airflow
AIRFLOW__CORE__DAGS_FOLDER=./data_pipeline/airflow/dags

# ========================================
# ML & MODEL SERVING
# ========================================
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=eip-models

# Model Inference
MODEL_INFERENCE_URL=http://localhost:8001
MODEL_CACHE_DIR=./ml/models/cache

# ========================================
# SECURITY
# ========================================
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["http://localhost:8501","http://localhost:3000"]
RATE_LIMIT_PER_MINUTE=100

# ========================================
# MONITORING & LOGGING
# ========================================
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=./logs/eip.log

PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Sentry (Error Tracking)
SENTRY_DSN=https://...@sentry.io/...

# ========================================
# EXTERNAL SERVICES
# ========================================
# News API
NEWS_API_KEY=your-key
NEWS_API_URL=https://newsapi.org/v2

# Alpha Vantage (Stock Data)
ALPHA_VANTAGE_KEY=your-key

# AWS (for production)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1
AWS_S3_BUCKET=eip-documents

# Email (SendGrid)
SENDGRID_API_KEY=your-key
EMAIL_FROM=noreply@eip.com

# ========================================
# FEATURE FLAGS
# ========================================
ENABLE_KAFKA_PIPELINE=true
ENABLE_SPARK_JOBS=true
ENABLE_AIRFLOW=true
ENABLE_ML_INFERENCE=true
ENABLE_GRAPHRAG=true
```

---

## 🐛 TROUBLESHOOTING

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'httpx'"

**Solution**:
```bash
pip install -r requirements.txt
# Or install specifically:
pip install httpx anthropic openai langchain streamlit fastapi
```

#### 2. "Connection refused" to databases

**Solution**:
```bash
# Check Docker services are running
docker-compose ps

# Restart services
docker-compose restart

# Check specific service logs
docker-compose logs postgres
docker-compose logs mongodb
docker-compose logs redis
```

#### 3. "Orchestrator fails to initialize"

**Solution**:
```bash
# Check if all agent files exist
ls -la agents/enhanced/

# Test individual agent import
python -c "from agents.enhanced.stock_analysis_agent import StockAnalysisAgent; print('OK')"

# Check for missing dependencies
pip list | grep langchain
```

#### 4. "API key not configured"

**Solution**:
```bash
# Verify .env file exists
cat .env | grep API_KEY

# Set environment variable manually
export OPENAI_API_KEY=sk-your-key

# Or in Python:
import os
os.environ['OPENAI_API_KEY'] = 'sk-your-key'
```

#### 5. Frontend doesn't connect to backend

**Solution**:
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS settings in .env
CORS_ORIGINS=["http://localhost:8501"]

# Restart backend with CORS enabled
```

#### 6. Kafka connection issues

**Solution**:
```bash
# Verify Kafka is running
docker-compose ps kafka

# Check Kafka logs
docker-compose logs kafka

# Disable Kafka temporarily in .env
ENABLE_KAFKA_PIPELINE=false
```

### Performance Issues

#### High Memory Usage

```bash
# Reduce number of workers
API_WORKERS=2  # in .env

# Reduce database connection pool
DATABASE_POOL_SIZE=10

# Clear Redis cache
redis-cli FLUSHALL
```

#### Slow Agent Responses

```bash
# Check LLM API latency
# Use faster model
OPENAI_MODEL=gpt-3.5-turbo  # instead of gpt-4

# Enable caching
ENABLE_REDIS_CACHE=true

# Reduce context window
MAX_CONTEXT_TOKENS=2000
```

---

## 📊 MONITORING & MAINTENANCE

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database connections
python -c "
from backend.app.models.database import engine
print('PostgreSQL:', engine.connect())
"

# Redis connection
redis-cli ping

# Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092
```

### Log Monitoring

```bash
# Backend logs
tail -f logs/eip.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Kubernetes logs
kubectl logs -f deployment/backend -n eip-production
```

### Metrics Dashboard

Access Grafana: http://localhost:3000 (if deployed)

**Key Metrics to Monitor**:
- Request latency (p50, p95, p99)
- Error rate
- Agent usage distribution
- LLM API costs
- Database query performance

---

## 🚀 DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Databases initialized
- [ ] All 35 agents tested
- [ ] API endpoints tested
- [ ] Security review completed
- [ ] API keys secured
- [ ] Backup strategy defined

### Production Deployment

- [ ] Infrastructure provisioned (Terraform)
- [ ] Kubernetes cluster ready
- [ ] Secrets configured
- [ ] Applications deployed
- [ ] Monitoring enabled
- [ ] Alerts configured
- [ ] Load balancer set up
- [ ] SSL certificates installed
- [ ] DNS configured
- [ ] Backup automated

### Post-Deployment

- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] Performance baselines established
- [ ] Documentation updated
- [ ] Team trained
- [ ] Incident response plan ready

---

## 📚 ADDITIONAL RESOURCES

### Documentation
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Architecture**: See `PROJECT_DESCRIPTION.md`
- **Agent Details**: See `COMPREHENSIVE_PROJECT_STATUS_ANALYSIS.md`

### Support
- **Issues**: Create GitHub issue
- **Email**: support@eip.com (if configured)

### Useful Commands

```bash
# Quick restart
docker-compose restart

# View all logs
docker-compose logs -f

# Clean restart
docker-compose down && docker-compose up -d

# Database backup
docker exec postgres pg_dump -U eip eip_db > backup.sql

# Database restore
docker exec -i postgres psql -U eip eip_db < backup.sql

# View running processes
docker-compose ps
kubectl get pods -n eip-production

# Scale deployment
kubectl scale deployment/backend --replicas=5 -n eip-production
```

---

## 🎉 CONGRATULATIONS!

You now have:
- ✅ **35 AI Agents** working together
- ✅ **Production-ready infrastructure**
- ✅ **Complete monitoring & logging**
- ✅ **Scalable Kubernetes deployment**
- ✅ **Comprehensive testing suite**

**Your EIP platform is ready to empower entrepreneurs worldwide!** 🚀

---

**Last Updated**: November 19, 2025
**Version**: 1.0
**Status**: Production Ready ✅
