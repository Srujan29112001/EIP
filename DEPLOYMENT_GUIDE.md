# 🚀 EIP - Complete Deployment Guide
**Entrepreneurship Intelligence Platform**
**Production Deployment Instructions**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Kubernetes Production Deployment](#kubernetes-production-deployment)
6. [Database Initialization](#database-initialization)
7. [Monitoring & Operations](#monitoring--operations)
8. [Troubleshooting](#troubleshooting)
9. [Security Checklist](#security-checklist)

---

## 1. Prerequisites

### Required Software
- **Python**: 3.11+
- **Node.js**: 18+
- **Docker**: 24.0+
- **Docker Compose**: 2.20+
- **kubectl**: 1.28+ (for K8s deployment)
- **Terraform**: 1.5+ (for cloud infrastructure)

### Required API Keys
- **OpenAI API Key**: For GPT-4o (primary LLM)
- **Anthropic API Key**: For Claude (optional, fallback)
- **DeepSeek API Key**: For DeepSeek-R1 (optional)

### Cloud Requirements (Production)
- **AWS Account** (or GCP/Azure)
- **Domain Name** (for production URL)
- **SSL Certificate** (Let's Encrypt or ACM)

---

## 2. Environment Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/Srujan29112001/EIP.git
cd EIP
```

### Step 2: Create Environment File

```bash
cp .env.example .env
```

### Step 3: Configure Environment Variables

Edit `.env` with your configuration:

```bash
# === CORE CONFIGURATION ===
ENVIRONMENT=production  # development|staging|production
DEBUG=false
SECRET_KEY=your-super-secret-key-change-this  # Generate: openssl rand -hex 32

# === API KEYS (REQUIRED) ===
OPENAI_API_KEY=sk-...your-openai-key
ANTHROPIC_API_KEY=sk-ant-...  # Optional
DEEPSEEK_API_KEY=sk-...  # Optional

# === DATABASE CONFIGURATION ===
# PostgreSQL (Main database)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eip_db
POSTGRES_USER=eip_user
POSTGRES_PASSWORD=change-this-password

# MongoDB (Documents)
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DB=eip_mongo
MONGO_USER=eip_user
MONGO_PASSWORD=change-this-password

# Redis (Cache/Sessions)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=change-this-password

# Neo4j (Knowledge Graph)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=change-this-password

# === KAFKA CONFIGURATION ===
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_NEWS=news_stream
KAFKA_TOPIC_MARKET=market_stream
KAFKA_TOPIC_POLICY=policy_stream

# === VECTOR STORE ===
VECTOR_STORE_PROVIDER=chroma  # chroma|pinecone
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Optional: Pinecone
# PINECONE_API_KEY=your-pinecone-key
# PINECONE_ENVIRONMENT=us-west1-gcp

# === APPLICATION SETTINGS ===
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
CORS_ORIGINS=http://localhost:8501,http://localhost:3000

# === MONITORING ===
LOG_LEVEL=INFO  # DEBUG|INFO|WARNING|ERROR
SENTRY_DSN=  # Optional: Sentry error tracking

# === SECURITY ===
JWT_SECRET=your-jwt-secret-key  # Generate: openssl rand -hex 32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# === RATE LIMITING ===
RATE_LIMIT_PER_MINUTE=100
```

---

## 3. Local Development

### Quick Start (5 minutes)

```bash
# 1. Install Python dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Start infrastructure with Docker Compose
docker-compose up -d postgres mongodb redis neo4j kafka zookeeper

# 3. Initialize databases
python scripts/init_db.py
python scripts/seed_knowledge_base.py

# 4. Start backend API
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. In another terminal, start frontend
cd frontend
streamlit run app.py --server.port 8501

# 6. Access the application
# - Frontend: http://localhost:8501
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Test All Agents

```bash
# Test all 21 AI agents
python scripts/test_all_agents.py

# Quick test (3 queries only)
python scripts/test_all_agents.py --quick
```

---

## 4. Docker Deployment

### Build Docker Images

```bash
# Build backend image
docker build -t eip-backend:latest -f infrastructure/docker/Dockerfile.backend .

# Build frontend image
docker build -t eip-frontend:latest -f infrastructure/docker/Dockerfile.frontend .
```

### Run with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Verify Deployment

```bash
# Check running containers
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test database connectivity
docker-compose exec backend python -c "from app.models import engine; print('DB Connected:', engine.connect())"
```

---

## 5. Kubernetes Production Deployment

### Prerequisites

1. **Kubernetes Cluster**:
   - AWS EKS, GCP GKE, or Azure AKS
   - At least 3 nodes (2 vCPUs, 8GB RAM each)

2. **kubectl configured**:
   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

### Step 1: Deploy Infrastructure with Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review plan
terraform plan -var="environment=production"

# Apply (create infrastructure)
terraform apply -var="environment=production"

# Note the outputs (RDS endpoint, EKS cluster name, etc.)
```

### Step 2: Configure kubectl for EKS

```bash
aws eks update-kubeconfig --name eip-production-eks --region us-east-1
```

### Step 3: Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace eip

# Create secrets from .env file
kubectl create secret generic eip-secrets \
  --from-env-file=.env \
  --namespace=eip

# Create secret for database passwords
kubectl create secret generic eip-db-secrets \
  --from-literal=postgres-password='your-postgres-password' \
  --from-literal=mongo-password='your-mongo-password' \
  --from-literal=redis-password='your-redis-password' \
  --from-literal=neo4j-password='your-neo4j-password' \
  --namespace=eip
```

### Step 4: Deploy Application

```bash
# Deploy databases (if not using managed services)
kubectl apply -f infrastructure/k8s/databases/ --namespace=eip

# Deploy backend
kubectl apply -f infrastructure/k8s/backend/ --namespace=eip

# Deploy frontend
kubectl apply -f infrastructure/k8s/frontend/ --namespace=eip

# Deploy monitoring
kubectl apply -f infrastructure/k8s/monitoring/ --namespace=eip
```

### Step 5: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n eip

# Check services
kubectl get svc -n eip

# Check ingress
kubectl get ingress -n eip

# View logs
kubectl logs -f deployment/eip-backend -n eip
```

### Step 6: Initialize Databases

```bash
# Run database initialization job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: eip-db-init
  namespace: eip
spec:
  template:
    spec:
      containers:
      - name: init
        image: eip-backend:latest
        command: ["python", "scripts/init_db.py"]
        envFrom:
        - secretRef:
            name: eip-secrets
      restartPolicy: Never
  backoffLimit: 3
EOF

# Check job status
kubectl logs job/eip-db-init -n eip
```

---

## 6. Database Initialization

### PostgreSQL Tables

```bash
# Initialize PostgreSQL schema
python scripts/init_db.py

# This creates:
# - users table
# - businesses table
# - portfolios table
# - queries table (chat history)
# - sessions table
```

### Neo4j Knowledge Graph

```bash
# Seed Neo4j with initial knowledge
python scripts/seed_knowledge_base.py

# This creates:
# - Policy nodes
# - Company nodes
# - Market nodes
# - Relationships between entities
```

### Vector Store (Chroma/Pinecone)

```bash
# Index initial documents for RAG
python scripts/seed_vector_store.py

# This indexes:
# - Policy documents
# - Market research reports
# - Legal precedents
# - Business cases
```

---

## 7. Monitoring & Operations

### Access Monitoring Dashboards

```bash
# Forward Grafana port
kubectl port-forward svc/grafana 3000:3000 -n eip

# Access Grafana at http://localhost:3000
# Default credentials: admin/admin (change on first login)
```

### Key Metrics to Monitor

1. **Application Metrics**:
   - Request latency (p50, p95, p99)
   - Error rate
   - Agent query success rate
   - Token usage (LLM costs)

2. **Infrastructure Metrics**:
   - CPU utilization
   - Memory usage
   - Pod restart count
   - Disk I/O

3. **Database Metrics**:
   - Connection pool usage
   - Query latency
   - Cache hit rate (Redis)

### View Logs

```bash
# Backend logs
kubectl logs -f deployment/eip-backend -n eip --tail=100

# Frontend logs
kubectl logs -f deployment/eip-frontend -n eip --tail=100

# All logs with label selector
kubectl logs -f -l app=eip -n eip
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment eip-backend --replicas=5 -n eip

# Horizontal Pod Autoscaler (HPA) already configured
kubectl get hpa -n eip

# HPA will auto-scale between 3-20 replicas based on CPU/memory
```

---

## 8. Troubleshooting

### Common Issues

#### 1. Backend Won't Start

**Symptom**: `ModuleNotFoundError` or `ImportError`

**Solution**:
```bash
# Verify Python dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Must be 3.11+

# Rebuild Docker image
docker-compose build backend
```

#### 2. Database Connection Failed

**Symptom**: `Could not connect to database`

**Solution**:
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection
psql -h localhost -U eip_user -d eip_db

# Check environment variables
echo $POSTGRES_HOST
```

#### 3. API Key Invalid

**Symptom**: `401 Unauthorized` from OpenAI/Anthropic

**Solution**:
```bash
# Verify API key in .env
grep OPENAI_API_KEY .env

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 4. Agent Returns Empty Response

**Symptom**: Chat returns "I apologize, but..."

**Solution**:
```bash
# Check backend logs
docker-compose logs backend

# Test agent directly
python scripts/test_all_agents.py --quick

# Verify LLM service
python -c "from backend.app.services.llm_service import LLMService; llm=LLMService(); print('OK')"
```

#### 5. Kafka Consumer Not Processing

**Symptom**: Messages sent but not consumed

**Solution**:
```bash
# Check Kafka is running
docker-compose ps kafka

# List topics
docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Check consumer groups
docker-compose exec kafka kafka-consumer-groups --list --bootstrap-server localhost:9092

# View consumer lag
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe --group news_consumer_group
```

---

## 9. Security Checklist

### Before Production Deployment

- [ ] **Change all default passwords** in `.env`
- [ ] **Generate new SECRET_KEY and JWT_SECRET** (use `openssl rand -hex 32`)
- [ ] **Enable HTTPS** with valid SSL certificate
- [ ] **Configure firewall rules** (only allow ports 80, 443)
- [ ] **Enable rate limiting** on API endpoints
- [ ] **Set up DDoS protection** (Cloudflare, AWS Shield)
- [ ] **Configure CORS** properly (only allow your frontend domain)
- [ ] **Enable database backups** (daily automated backups)
- [ ] **Set up error monitoring** (Sentry, DataDog)
- [ ] **Enable audit logging** for sensitive operations
- [ ] **Rotate API keys** regularly (90-day policy)
- [ ] **Set up alerting** for critical errors
- [ ] **Review IAM permissions** (principle of least privilege)
- [ ] **Enable encryption at rest** for databases
- [ ] **Configure VPC security groups** properly

---

## 10. Backup & Disaster Recovery

### Automated Backups

```bash
# PostgreSQL backup (daily)
pg_dump -h localhost -U eip_user eip_db > backup_$(date +%Y%m%d).sql

# MongoDB backup
mongodump --uri="mongodb://eip_user:password@localhost:27017/eip_mongo" --out=/backups/mongo_$(date +%Y%m%d)

# Neo4j backup
docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j_$(date +%Y%m%d).dump
```

### Restore from Backup

```bash
# PostgreSQL restore
psql -h localhost -U eip_user eip_db < backup_20251119.sql

# MongoDB restore
mongorestore --uri="mongodb://eip_user:password@localhost:27017/" /backups/mongo_20251119

# Neo4j restore
docker-compose exec neo4j neo4j-admin load --database=neo4j --from=/backups/neo4j_20251119.dump
```

---

## 11. Cost Optimization

### LLM API Costs

- **GPT-4o**: ~$0.01 per query (with caching)
- **Claude**: ~$0.015 per query
- **DeepSeek-R1**: ~$0.002 per query

**Optimization Tips**:
1. Enable response caching (implemented)
2. Use DeepSeek for simple queries
3. Set max_tokens limits
4. Implement query deduplication

### Infrastructure Costs (AWS)

**Development** (~$150/month):
- EKS: $75
- RDS: $30
- ElastiCache: $20
- S3: $10
- Other: $15

**Production** (~$500/month):
- EKS (5 nodes): $250
- RDS (Multi-AZ): $150
- ElastiCache: $50
- S3 + CloudFront: $30
- Other: $20

---

## 12. Performance Tuning

### Backend Optimization

```python
# Enable connection pooling
# In backend/app/models/database.py

SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 40
SQLALCHEMY_POOL_TIMEOUT = 30
```

### Redis Caching

```python
# Cache agent responses for 1 hour
@cache(ttl=3600, key_prefix="agent_response")
async def get_agent_response(query: str):
    ...
```

### Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_queries_user_id ON queries(user_id);
CREATE INDEX idx_queries_created_at ON queries(created_at DESC);
CREATE INDEX idx_portfolios_user_id ON portfolios(user_id);
```

---

## 13. Support & Maintenance

### Regular Maintenance Tasks

**Daily**:
- Check error logs
- Monitor API costs
- Review user feedback

**Weekly**:
- Update dependencies (`pip list --outdated`)
- Review security alerts
- Optimize slow queries
- Clear old logs

**Monthly**:
- Rotate API keys
- Review and optimize costs
- Update documentation
- Security audit

---

## 🎉 Deployment Complete!

### Post-Deployment Checklist

- [ ] All services running
- [ ] Databases initialized
- [ ] Test queries working
- [ ] Monitoring dashboards accessible
- [ ] Backups configured
- [ ] Alerts set up
- [ ] Documentation updated
- [ ] Team trained on operations

### Access URLs

- **Production Frontend**: https://eip.yourdomain.com
- **API**: https://api.eip.yourdomain.com
- **API Docs**: https://api.eip.yourdomain.com/docs
- **Grafana**: https://grafana.eip.yourdomain.com

### Need Help?

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Email**: support@eip-platform.com

---

**Deployment Guide Version**: 1.0
**Last Updated**: November 19, 2025
**Maintained By**: EIP Engineering Team
