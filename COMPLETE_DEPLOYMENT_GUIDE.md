# 🚀 EIP Complete Deployment Guide

**Entrepreneurship Intelligence Platform - Production Deployment**

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Infrastructure Setup](#infrastructure-setup)
3. [Application Deployment](#application-deployment)
4. [ML Models Deployment](#ml-models-deployment)
5. [Mobile App Deployment](#mobile-app-deployment)
6. [Monitoring & Operations](#monitoring--operations)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Terraform** >= 1.0
- **kubectl** >= 1.28
- **Docker** >= 24.0
- **AWS CLI** v2
- **Node.js** >= 18
- **Python** >= 3.11
- **Git**

### Required Accounts

- AWS Account with admin access
- Domain name (for production)
- OpenAI API key
- (Optional) Anthropic, DeepSeek API keys

---

## Infrastructure Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd EIP
```

### Step 2: Configure AWS Credentials

```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region
```

### Step 3: Deploy Infrastructure with Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Create terraform.tfvars file
cat > terraform.tfvars <<EOF
environment = "production"
aws_region  = "us-east-1"

# Database passwords (use strong, random passwords)
db_password      = "$(openssl rand -base64 32)"
mongodb_password = "$(openssl rand -base64 32)"
neo4j_password   = "$(openssl rand -base64 32)"

# EKS configuration
eks_node_desired_size = 5
eks_node_min_size     = 3
eks_node_max_size     = 10
eks_node_instance_type = "t3.large"

# Database configurations
rds_instance_class      = "db.r5.large"
rds_allocated_storage   = 200
redis_node_type         = "cache.r5.large"
mongodb_instance_class  = "db.r5.large"
neo4j_instance_type     = "r5.xlarge"
EOF

# Plan deployment
terraform plan -var-file="terraform.tfvars"

# Apply infrastructure
terraform apply -var-file="terraform.tfvars"

# Save outputs
terraform output -json > outputs.json
```

### Step 4: Configure kubectl for EKS

```bash
aws eks update-kubeconfig --name $(terraform output -raw eks_cluster_name) --region us-east-1

# Verify access
kubectl get nodes
```

---

## Application Deployment

### Step 1: Build Docker Images

```bash
# Backend
docker build -t eip-backend:latest -f infrastructure/docker/Dockerfile.backend .
docker tag eip-backend:latest <your-ecr-repo>/eip-backend:latest
docker push <your-ecr-repo>/eip-backend:latest

# Frontend
docker build -t eip-frontend:latest -f infrastructure/docker/Dockerfile.frontend .
docker tag eip-frontend:latest <your-ecr-repo>/eip-frontend:latest
docker push <your-ecr-repo>/eip-frontend:latest
```

### Step 2: Create Kubernetes Secrets

```bash
# Create namespace
kubectl create namespace eip

# Database credentials
kubectl create secret generic eip-db-credentials \
  --from-literal=postgres-password=$(terraform output -raw db_password) \
  --from-literal=mongodb-password=$(terraform output -raw mongodb_password) \
  --from-literal=neo4j-password=$(terraform output -raw neo4j_password) \
  --from-literal=redis-host=$(terraform output -raw redis_endpoint) \
  -n eip

# API keys
kubectl create secret generic eip-api-keys \
  --from-literal=openai-api-key=$OPENAI_API_KEY \
  --from-literal=anthropic-api-key=$ANTHROPIC_API_KEY \
  -n eip

# Database connection strings
kubectl create secret generic eip-db-connections \
  --from-literal=database-url="postgresql://eip_admin:$(terraform output -raw db_password)@$(terraform output -raw rds_endpoint)/eip" \
  --from-literal=mongodb-url="mongodb://eip_admin:$(terraform output -raw mongodb_password)@$(terraform output -raw mongodb_endpoint)" \
  --from-literal=neo4j-uri="bolt://$(terraform output -raw neo4j_private_ip):7687" \
  -n eip
```

### Step 3: Deploy to Kubernetes

```bash
cd infrastructure/k8s

# Update image tags in deployments
export BACKEND_IMAGE="<your-ecr-repo>/eip-backend:latest"
export FRONTEND_IMAGE="<your-ecr-repo>/eip-frontend:latest"

# Apply configurations
kubectl apply -f configmaps/ -n eip
kubectl apply -f deployments/ -n eip
kubectl apply -f services/ -n eip
kubectl apply -f ingress/ -n eip

# Wait for deployments
kubectl rollout status deployment/eip-backend -n eip
kubectl rollout status deployment/eip-frontend -n eip
```

### Step 4: Initialize Databases

```bash
# Port forward to backend pod
kubectl port-forward -n eip deployment/eip-backend 8000:8000 &

# Initialize PostgreSQL
python scripts/init_db.py

# Seed knowledge bases
python scripts/seed_knowledge_base.py

# Stop port forward
kill %1
```

### Step 5: Configure Ingress & DNS

```bash
# Get load balancer address
kubectl get ingress -n eip

# Update DNS records
# Point your domain to the load balancer address
# Example: eip.yourdomain.com -> <load-balancer-dns>

# Install cert-manager for SSL
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create certificate issuer
kubectl apply -f infrastructure/k8s/cert-issuer.yaml -n eip
```

---

## ML Models Deployment

### Step 1: Build ML Model Server

```bash
# Build Docker image
docker build -t eip-ml-server:latest -f ml/Dockerfile .
docker tag eip-ml-server:latest <your-ecr-repo>/eip-ml-server:latest
docker push <your-ecr-repo>/eip-ml-server:latest
```

### Step 2: Deploy ML Server

```bash
# Create deployment for ML server
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eip-ml-server
  namespace: eip
spec:
  replicas: 2
  selector:
    matchLabels:
      app: eip-ml-server
  template:
    metadata:
      labels:
        app: eip-ml-server
    spec:
      containers:
      - name: ml-server
        image: <your-ecr-repo>/eip-ml-server:latest
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "4Gi"
            cpu: "2000m"
          limits:
            memory: "8Gi"
            cpu: "4000m"
---
apiVersion: v1
kind: Service
metadata:
  name: eip-ml-server
  namespace: eip
spec:
  selector:
    app: eip-ml-server
  ports:
  - port: 8001
    targetPort: 8001
EOF
```

### Step 3: Download Pre-trained Models

```bash
# SSH into ML server pod
kubectl exec -it -n eip deployment/eip-ml-server -- bash

# Download models
python -c "
from transformers import AutoTokenizer, AutoModel
AutoTokenizer.from_pretrained('distilbert-base-uncased')
AutoModel.from_pretrained('distilbert-base-uncased')
AutoTokenizer.from_pretrained('ProsusAI/finbert')
AutoModel.from_pretrained('ProsusAI/finbert')
"
```

---

## Mobile App Deployment

### Step 1: Build Android APK

```bash
cd mobile

# Install dependencies
npm install

# Build Android
cd android
./gradlew assembleRelease

# APK location: android/app/build/outputs/apk/release/app-release.apk
```

### Step 2: Build iOS IPA

```bash
cd mobile/ios

# Install pods
pod install

# Build (requires Xcode)
xcodebuild -workspace EIP.xcworkspace \
  -scheme EIP \
  -configuration Release \
  -archivePath build/EIP.xcarchive \
  archive

# Create IPA
xcodebuild -exportArchive \
  -archivePath build/EIP.xcarchive \
  -exportPath build \
  -exportOptionsPlist ExportOptions.plist
```

### Step 3: Deploy to App Stores

**Google Play:**
1. Create release in Google Play Console
2. Upload APK
3. Fill in store listing
4. Submit for review

**App Store:**
1. Create app in App Store Connect
2. Upload IPA via Xcode or Transporter
3. Fill in app information
4. Submit for review

---

## Monitoring & Operations

### Step 1: Deploy Prometheus & Grafana

```bash
# Add Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n eip

# Access Grafana
kubectl port-forward -n eip svc/prometheus-grafana 3000:80

# Default credentials: admin / prom-operator
```

### Step 2: Configure Alerts

```bash
# Apply alert rules
kubectl apply -f infrastructure/monitoring/alert-rules.yaml -n eip

# Configure PagerDuty/Slack webhooks
kubectl apply -f infrastructure/monitoring/alertmanager-config.yaml -n eip
```

### Step 3: Setup Logging (ELK Stack)

```bash
# Deploy Elasticsearch
helm install elasticsearch elastic/elasticsearch -n eip

# Deploy Kibana
helm install kibana elastic/kibana -n eip

# Deploy Filebeat
kubectl apply -f infrastructure/monitoring/filebeat-config.yaml -n eip
```

### Step 4: Setup Backup Jobs

```bash
# PostgreSQL backup job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: eip
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: pg-backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - |
              pg_dump \$DATABASE_URL | gzip > /backup/eip-\$(date +%Y%m%d).sql.gz
              aws s3 cp /backup/eip-\$(date +%Y%m%d).sql.gz s3://eip-backups/postgres/
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: eip-db-connections
                  key: database-url
          restartPolicy: OnFailure
EOF
```

---

## Verification & Testing

### Step 1: Health Checks

```bash
# Backend health
curl https://api.eip.yourdomain.com/health

# Frontend
curl https://eip.yourdomain.com

# ML Server
kubectl exec -n eip deployment/eip-backend -- curl http://eip-ml-server:8001/health
```

### Step 2: Run Integration Tests

```bash
# Set test environment
export API_URL=https://api.eip.yourdomain.com

# Run tests
pytest tests/integration/ -v
```

### Step 3: Load Testing

```bash
# Install k6
brew install k6  # macOS
# or download from https://k6.io

# Run load test
k6 run tests/performance/load-test.js
```

---

## Troubleshooting

### Common Issues

**1. Pods not starting**
```bash
# Check pod status
kubectl get pods -n eip

# Check logs
kubectl logs -n eip deployment/eip-backend

# Check events
kubectl describe pod -n eip <pod-name>
```

**2. Database connection issues**
```bash
# Verify secrets
kubectl get secret eip-db-connections -n eip -o yaml

# Test connection from pod
kubectl exec -it -n eip deployment/eip-backend -- bash
psql $DATABASE_URL
```

**3. High resource usage**
```bash
# Check resource metrics
kubectl top pods -n eip
kubectl top nodes

# Scale up if needed
kubectl scale deployment eip-backend --replicas=10 -n eip
```

**4. SSL certificate issues**
```bash
# Check certificate status
kubectl get certificate -n eip

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

---

## Scaling Guide

### Horizontal Scaling

```bash
# Scale backend
kubectl scale deployment eip-backend --replicas=10 -n eip

# Enable HPA
kubectl autoscale deployment eip-backend --min=3 --max=20 --cpu-percent=70 -n eip
```

### Vertical Scaling

```bash
# Update resource limits in deployment YAML
kubectl edit deployment eip-backend -n eip

# Increase to:
# requests: cpu=2, memory=4Gi
# limits: cpu=4, memory=8Gi
```

---

## Maintenance

### Updating Application

```bash
# Build new image
docker build -t eip-backend:v2.0.0 .
docker push <your-ecr-repo>/eip-backend:v2.0.0

# Rolling update
kubectl set image deployment/eip-backend eip-backend=<your-ecr-repo>/eip-backend:v2.0.0 -n eip

# Monitor rollout
kubectl rollout status deployment/eip-backend -n eip

# Rollback if needed
kubectl rollout undo deployment/eip-backend -n eip
```

### Database Migrations

```bash
# Run migrations
kubectl exec -it -n eip deployment/eip-backend -- alembic upgrade head
```

---

## Security Checklist

- [ ] All secrets stored in Kubernetes secrets
- [ ] SSL/TLS enabled for all endpoints
- [ ] Database encryption at rest enabled
- [ ] Network policies configured
- [ ] RBAC properly configured
- [ ] Security groups restrict access
- [ ] API rate limiting enabled
- [ ] Regular security audits scheduled
- [ ] Backup and disaster recovery tested

---

## Support & Resources

- **Documentation**: https://docs.eip.yourdomain.com
- **API Docs**: https://api.eip.yourdomain.com/docs
- **Status Page**: https://status.eip.yourdomain.com
- **Support**: support@eip.yourdomain.com

---

**Deployment Complete! 🎉**

Your EIP platform is now live and ready to help entrepreneurs succeed.
