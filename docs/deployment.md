# Deployment Guide

## Overview

This guide covers deployment options for the SynTeCX House Price Prediction platform.

## Prerequisites

### Local Development
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.9+ (for backend development)

### Production Deployment
- Cloud provider account (AWS, Azure, GCP)
- Domain name (optional)
- SSL certificate (recommended)

## Development Deployment

### Docker Compose (Recommended for Development)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd syntecx_hub
```

2. **Start all services:**
```bash
docker-compose up --build
```

3. **Access the services:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432
- Redis: localhost:6379

4. **Stop services:**
```bash
docker-compose down
```

### Manual Development Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Production Deployment

### Docker Deployment

#### 1. Build Production Images

Create production Dockerfiles:

**backend/Dockerfile.prod:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create necessary directories
RUN mkdir -p ml/models ml/data logs

# Run as non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run application
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
```

**frontend/Dockerfile.prod:**
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/out /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 2. Environment Configuration

Create `.env.production`:
```bash
# Database
DATABASE_URL=postgresql://user:password@db:5432/syntecx_hub
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_CACHE_TTL=7200

# Security
SECRET_KEY=your-production-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_V1_STR=/api/v1
PROJECT_NAME=SynTeCX House Price Prediction API
VERSION=1.0.0
DEBUG=False

# CORS
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]
```

#### 3. Production docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - DEBUG=${DEBUG}
    volumes:
      - ./backend/ml/models:/app/ml/models:ro
      - ./backend/logs:/app/logs
    depends_on:
      - db
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    ports:
      - "80:80"
      - "443:443"
    environment:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=syntecx_hub
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Cloud Deployment Options

#### AWS Deployment

**Using ECS with Fargate:**

1. **Create ECR repositories:**
```bash
aws ecr create-repository --repository-name syntecx-backend
aws ecr create-repository --repository-name syntecx-frontend
```

2. **Build and push images:**
```bash
# Backend
docker build -t syntecx-backend -f backend/Dockerfile.prod backend/
docker tag syntecx-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/syntecx-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/syntecx-backend:latest

# Frontend
docker build -t syntecx-frontend -f frontend/Dockerfile.prod frontend/
docker tag syntecx-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/syntecx-frontend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/syntecx-frontend:latest
```

3. **Create ECS Task Definitions:**
```json
{
  "family": "syntecx-backend",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.<region>.amazonaws.com/syntecx-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/syntecx-backend",
          "awslogs-region": "<region>",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

4. **Deploy with Terraform:**
```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

module "syntecx_platform" {
  source = "./modules/ecs-fargate"
  
  app_name    = "syntecx-hub"
  environment = "production"
  
  backend_image = var.backend_image
  frontend_image = var.frontend_image
  
  database_url = var.database_url
  redis_url    = var.redis_url
}
```

#### Azure Deployment

**Using Azure Container Instances:**

```bash
# Create resource group
az group create --name syntecx-rg --location eastus

# Create container registry
az acr create --resource-group syntecx-rg --name syntecxRegistry --sku Basic

# Build and push images
az acr build --image syntecx-backend:latest --registry syntecxRegistry --file backend/Dockerfile.prod backend/
az acr build --image syntecx-frontend:latest --registry syntecxRegistry --file frontend/Dockerfile.prod frontend/

# Deploy containers
az container create \
  --resource-group syntecx-rg \
  --name syntecx-backend \
  --image syntecxRegistry.azurecr.io/syntecx-backend:latest \
  --dns-name-label syntecx-api \
  --ports 8000 \
  --environment-variables DATABASE_URL=$DATABASE_URL

az container create \
  --resource-group syntecx-rg \
  --name syntecx-frontend \
  --image syntecxRegistry.azurecr.io/syntecx-frontend:latest \
  --dns-name-label syntecx-app \
  --ports 80
```

#### Google Cloud Deployment

**Using Cloud Run:**

```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/$PROJECT_ID/syntecx-backend backend/
gcloud builds submit --tag gcr.io/$PROJECT_ID/syntecx-frontend frontend/

# Deploy to Cloud Run
gcloud run deploy syntecx-backend \
  --image gcr.io/$PROJECT_ID/syntecx-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DATABASE_URL

gcloud run deploy syntecx-frontend \
  --image gcr.io/$PROJECT_ID/syntecx-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Kubernetes Deployment

**Create deployment manifests:**

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: syntecx-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: syntecx-backend
  template:
    metadata:
      labels:
        app: syntecx-backend
    spec:
      containers:
      - name: backend
        image: syntecx/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: syntecx-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: syntecx-backend-service
spec:
  selector:
    app: syntecx-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Monitoring and Logging

#### Health Checks

**Backend Health Endpoint:**
```
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "SynTeCX House Price Prediction API",
  "version": "1.0.0",
  "components": {
    "api": {"status": "healthy"},
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"}
  }
}
```

#### Logging Configuration

**Production logging in `backend/app/core/logging.py`:**
```python
logger.add(
    "logs/production.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO",
    rotation="100 MB",
    retention="30 days",
    compression="zip"
)
```

#### Monitoring Setup

**Prometheus metrics endpoint:**
```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
prediction_counter = Counter('predictions_total', 'Total predictions made')
prediction_duration = Histogram('prediction_duration_seconds', 'Prediction duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Security Considerations

#### Environment Variables
Never commit secrets to version control. Use:
- `.env` files for development (add to `.gitignore`)
- Secret management services for production
- AWS Secrets Manager, Azure Key Vault, or GCP Secret Manager

#### SSL/TLS Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/certificate.crt;
    ssl_certificate_key /etc/nginx/ssl/private.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Backup and Recovery

#### Database Backup
```bash
# PostgreSQL backup
pg_dump -h db -U user -d syntecx_hub > backup_$(date +%Y%m%d).sql

# Restore
psql -h db -U user -d syntecx_hub < backup_20240115.sql
```

#### Model Artifacts Backup
```bash
# Backup model files
tar -czf models_backup_$(date +%Y%m%d).tar.gz backend/ml/models/

# Store in cloud storage
aws s3 cp models_backup_20240115.tar.gz s3://syntecx-backups/
```

### CI/CD Pipeline

**GitHub Actions example:**
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push backend
      run: |
        docker build -t ${{ secrets.DOCKER_REGISTRY }}/syntecx-backend:${{ github.sha }} backend/
        docker push ${{ secrets.DOCKER_REGISTRY }}/syntecx-backend:${{ github.sha }}
    
    - name: Deploy to production
      run: |
        # Deployment commands here
        kubectl set image deployment/syntecx-backend backend=${{ secrets.DOCKER_REGISTRY }}/syntecx-backend:${{ github.sha }}
```

This deployment guide provides comprehensive instructions for running the SynTeCX House Price Prediction platform in development and production environments.