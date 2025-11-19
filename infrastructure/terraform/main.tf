/**
 * EIP Infrastructure - Main Terraform Configuration
 * Provisions complete infrastructure on AWS for Entrepreneurship Intelligence Platform
 */

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    bucket = "eip-terraform-state"
    key    = "eip/terraform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "eip-terraform-locks"
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "EIP"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Local variables
locals {
  cluster_name = "eip-${var.environment}"
  common_tags = {
    Project     = "EIP"
    Environment = var.environment
  }
}

# VPC and Networking
module "networking" {
  source = "./modules/networking"

  environment  = var.environment
  vpc_cidr     = var.vpc_cidr
  azs          = var.availability_zones
  cluster_name = local.cluster_name
  tags         = local.common_tags
}

# EKS Cluster (Kubernetes)
module "eks" {
  source = "./modules/eks"

  environment        = var.environment
  cluster_name       = local.cluster_name
  cluster_version    = var.eks_cluster_version
  vpc_id             = module.networking.vpc_id
  subnet_ids         = module.networking.private_subnet_ids
  node_desired_size  = var.eks_node_desired_size
  node_min_size      = var.eks_node_min_size
  node_max_size      = var.eks_node_max_size
  node_instance_type = var.eks_node_instance_type
  tags               = local.common_tags
}

# RDS PostgreSQL (Main Database)
module "rds" {
  source = "./modules/rds"

  environment         = var.environment
  identifier          = "eip-${var.environment}"
  engine_version      = "15.4"
  instance_class      = var.rds_instance_class
  allocated_storage   = var.rds_allocated_storage
  database_name       = "eip"
  master_username     = var.db_username
  master_password     = var.db_password
  vpc_id              = module.networking.vpc_id
  subnet_ids          = module.networking.database_subnet_ids
  multi_az            = var.environment == "production" ? true : false
  backup_retention    = var.environment == "production" ? 7 : 1
  tags                = local.common_tags
}

# ElastiCache Redis (Caching & Session Management)
module "redis" {
  source = "./modules/redis"

  environment          = var.environment
  cluster_id           = "eip-${var.environment}"
  engine_version       = "7.0"
  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_nodes
  parameter_group_name = "default.redis7"
  vpc_id               = module.networking.vpc_id
  subnet_ids           = module.networking.database_subnet_ids
  tags                 = local.common_tags
}

# DocumentDB (MongoDB Compatible)
module "mongodb" {
  source = "./modules/mongodb"

  environment       = var.environment
  cluster_identifier = "eip-${var.environment}"
  engine_version    = "5.0"
  instance_class    = var.mongodb_instance_class
  instance_count    = var.mongodb_instance_count
  master_username   = var.mongodb_username
  master_password   = var.mongodb_password
  vpc_id            = module.networking.vpc_id
  subnet_ids        = module.networking.database_subnet_ids
  tags              = local.common_tags
}

# EC2 Instance for Neo4j (Knowledge Graph)
module "neo4j" {
  source = "./modules/neo4j"

  environment     = var.environment
  instance_type   = var.neo4j_instance_type
  volume_size     = var.neo4j_volume_size
  neo4j_password  = var.neo4j_password
  vpc_id          = module.networking.vpc_id
  subnet_id       = module.networking.private_subnet_ids[0]
  tags            = local.common_tags
}

# S3 Buckets (Data Storage)
module "s3" {
  source = "./modules/s3"

  environment = var.environment
  tags        = local.common_tags
}

# Outputs
output "eks_cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "eks_cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.redis.endpoint
  sensitive   = true
}

output "mongodb_endpoint" {
  description = "DocumentDB cluster endpoint"
  value       = module.mongodb.endpoint
  sensitive   = true
}

output "neo4j_private_ip" {
  description = "Neo4j private IP address"
  value       = module.neo4j.private_ip
  sensitive   = true
}

output "s3_buckets" {
  description = "Created S3 buckets"
  value       = module.s3.buckets
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.networking.vpc_id
}
