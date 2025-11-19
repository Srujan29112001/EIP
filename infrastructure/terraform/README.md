# EIP Terraform Infrastructure

Infrastructure as Code for Entrepreneurship Intelligence Platform using Terraform.

## Architecture

This Terraform configuration deploys the complete EIP infrastructure on AWS:

- **EKS Cluster**: Kubernetes cluster for running containerized applications
- **RDS PostgreSQL**: Main relational database (OLTP)
- **ElastiCache Redis**: Caching and session management
- **DocumentDB**: MongoDB-compatible document database
- **Neo4j**: Knowledge graph database (on EC2)
- **S3 Buckets**: Object storage for data lake and artifacts
- **VPC**: Isolated network with public/private subnets

## Prerequisites

- Terraform >= 1.0
- AWS CLI configured with credentials
- kubectl (for EKS management)

## Directory Structure

```
terraform/
├── main.tf                 # Main configuration
├── variables.tf            # Input variables
├── outputs.tf             # Output values
├── terraform.tfvars       # Variable values (not in git)
├── modules/
│   ├── eks/               # EKS cluster
│   ├── rds/               # PostgreSQL database
│   ├── redis/             # Redis cache
│   ├── mongodb/           # DocumentDB
│   ├── neo4j/             # Neo4j graph database
│   ├── s3/                # S3 buckets
│   └── networking/        # VPC, subnets, etc.
└── environments/
    ├── dev.tfvars
    ├── staging.tfvars
    └── production.tfvars
```

## Usage

### 1. Initialize Terraform

```bash
cd infrastructure/terraform
terraform init
```

### 2. Create terraform.tfvars

```hcl
# terraform.tfvars
environment = "dev"
aws_region  = "us-east-1"

# Database credentials (use secure secrets management in production)
db_password      = "your-secure-password"
mongodb_password = "your-secure-password"
neo4j_password   = "your-secure-password"
```

### 3. Plan Infrastructure

```bash
terraform plan -var-file="terraform.tfvars"
```

### 4. Apply Infrastructure

```bash
terraform apply -var-file="terraform.tfvars"
```

### 5. Get Outputs

```bash
terraform output
```

## Environment-Specific Deployment

### Development

```bash
terraform apply -var-file="environments/dev.tfvars"
```

### Staging

```bash
terraform apply -var-file="environments/staging.tfvars"
```

### Production

```bash
terraform apply -var-file="environments/production.tfvars"
```

## EKS Cluster Access

After deployment, configure kubectl:

```bash
aws eks update-kubeconfig --name $(terraform output -raw eks_cluster_name) --region us-east-1
```

Verify access:

```bash
kubectl get nodes
```

## Connecting to Databases

### PostgreSQL (RDS)

```bash
psql -h $(terraform output -raw rds_endpoint | cut -d: -f1) -U eip_admin -d eip
```

### Redis

```bash
redis-cli -h $(terraform output -raw redis_endpoint | cut -d: -f1)
```

### MongoDB (DocumentDB)

```bash
mongo --ssl --host $(terraform output -raw mongodb_endpoint | cut -d: -f1) \
  --sslCAFile rds-combined-ca-bundle.pem \
  --username eip_admin --password <password>
```

### Neo4j

```bash
# Connect via private IP (from within VPC or via bastion)
cypher-shell -a bolt://$(terraform output -raw neo4j_private_ip):7687 \
  -u neo4j -p <password>
```

## Resource Costs (Estimated)

**Development Environment:**
- EKS Cluster: ~$73/month
- t3.large nodes (3): ~$150/month
- RDS db.t3.medium: ~$60/month
- Redis cache.t3.medium (2): ~$80/month
- DocumentDB db.t3.medium (2): ~$120/month
- Neo4j t3.xlarge: ~$120/month
- **Total: ~$600/month**

**Production Environment:**
- EKS Cluster: ~$73/month
- t3.large nodes (5-10): ~$250-500/month
- RDS db.r5.large (Multi-AZ): ~$350/month
- Redis cache.r5.large (3): ~$450/month
- DocumentDB db.r5.large (3): ~$650/month
- Neo4j r5.xlarge: ~$350/month
- S3 storage: ~$50/month
- **Total: ~$2,200-2,500/month**

## Security Best Practices

1. **Secrets Management**: Use AWS Secrets Manager or Parameter Store for passwords
2. **Network Security**: All databases in private subnets
3. **Encryption**: Enable encryption at rest for all data stores
4. **Access Control**: Use IAM roles and policies
5. **Monitoring**: Enable CloudWatch logs and metrics

## Backup & Disaster Recovery

- **RDS**: Automated daily backups (7-day retention in production)
- **DocumentDB**: Automated daily backups
- **Neo4j**: EBS snapshots
- **S3**: Versioning enabled

## Scaling

### EKS Cluster Autoscaling

```bash
# Update node group size
terraform apply -var="eks_node_desired_size=5"
```

### Database Scaling

Modify instance class in terraform.tfvars and apply.

## Cleanup

**Warning**: This will destroy all infrastructure!

```bash
terraform destroy -var-file="terraform.tfvars"
```

## Troubleshooting

### EKS Access Issues

```bash
# Update kubeconfig
aws eks update-kubeconfig --name eip-dev --region us-east-1

# Check cluster status
aws eks describe-cluster --name eip-dev
```

### Database Connection Issues

- Verify security groups allow inbound traffic
- Check VPC routing and NAT gateway
- Ensure credentials are correct

## Monitoring

After deployment, access:
- **Prometheus**: http://<load-balancer>:9090
- **Grafana**: http://<load-balancer>:3000
- **EKS Dashboard**: via kubectl proxy

## Support

For issues, see main project documentation or contact DevOps team.
