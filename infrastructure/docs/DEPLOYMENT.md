# 🚀 Deployment Guide

## Smart News Aggregator - Production Deployment

---

## 📋 Prerequisites

### Required Software
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Kubernetes (optional, for K8s deployment)
- kubectl (optional)

### System Requirements

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 50 GB SSD
- Network: 100 Mbps

**Recommended:**
- CPU: 8 cores
- RAM: 16 GB
- Disk: 200 GB SSD
- Network: 1 Gbps

---

## 🔧 Pre-Deployment Checklist

- [ ] Clone repository
- [ ] Configure environment variables
- [ ] Setup database credentials
- [ ] Configure API keys
- [ ] Setup SSL certificates
- [ ] Configure domain/DNS
- [ ] Setup monitoring
- [ ] Configure backups
- [ ] Test deployment locally

---

## 🌍 Deployment Methods

### Method 1: Docker Compose (Recommended for Small-Medium Scale)

#### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/smart-news-aggregator.git
cd smart-news-aggregator
```

#### Step 2: Configure Environment
```bash
# Copy example env files
cp backend/.env.example backend/.env
cp ml_service/.env.example ml_service/.env
cp scraper_service/.env.example scraper_service/.env
cp frontend/.env.local.example frontend/.env.local

# Edit environment files
nano backend/.env
nano ml_service/.env
nano scraper_service/.env
nano frontend/.env.local
```

#### Step 3: Update Production Config
```bash
# Edit docker-compose.prod.yml
nano docker-compose.prod.yml

# Update:
# - Image tags
# - Resource limits
# - Network settings
# - Volume paths
```

#### Step 4: Build Images
```bash
# Build all images
docker-compose -f docker-compose.prod.yml build

# Or use Makefile
make build
```

#### Step 5: Deploy
```bash
# Start all services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

#### Step 6: Initialize Database
```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Seed data
docker-compose -f docker-compose.prod.yml exec backend python scripts/seed_data.py
```

#### Step 7: Verify Deployment
```bash
# Check service health
make health

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

---

### Method 2: Kubernetes (Recommended for Large Scale)

#### Step 1: Prepare Cluster
```bash
# Create namespace
kubectl create namespace smart-news

# Setup secrets
kubectl create secret generic db-secrets \
  --from-literal=password='your-db-password' \
  -n smart-news

kubectl create secret generic api-secrets \
  --from-literal=news-api-key='your-api-key' \
  -n smart-news
```

#### Step 2: Build and Push Images
```bash
# Build images
docker build -f infrastructure/docker/backend.Dockerfile -t registry.example.com/smart-news/backend:v1.0.0 .
docker build -f infrastructure/docker/ml.Dockerfile -t registry.example.com/smart-news/ml-service:v1.0.0 .
docker build -f infrastructure/docker/scraper.Dockerfile -t registry.example.com/smart-news/scraper:v1.0.0 .

# Push to registry
docker push registry.example.com/smart-news/backend:v1.0.0
docker push registry.example.com/smart-news/ml-service:v1.0.0
docker push registry.example.com/smart-news/scraper:v1.0.0
```

#### Step 3: Deploy with Kustomize
```bash
# Production deployment
kubectl apply -k infrastructure/kubernetes/overlays/production

# Check rollout status
kubectl rollout status deployment/backend -n smart-news
kubectl rollout status deployment/ml-service -n smart-news
kubectl rollout status deployment/frontend -n smart-news
```

#### Step 4: Verify Deployment
```bash
# Check pods
kubectl get pods -n smart-news

# Check services
kubectl get svc -n smart-news

# View logs
kubectl logs -f deployment/backend -n smart-news
```

---

## 🔐 Security Configuration

### SSL/TLS Setup

#### Option 1: Let's Encrypt
```bash
# Install certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem infrastructure/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem infrastructure/nginx/ssl/
```

#### Option 2: Manual Certificate
```bash
# Place your certificates in:
infrastructure/nginx/ssl/fullchain.pem
infrastructure/nginx/ssl/privkey.pem
```

### Firewall Configuration
```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

---

## 📊 Monitoring Setup

### Prometheus & Grafana

```bash
# Start monitoring stack
docker-compose -f infrastructure/monitoring/docker-compose.yml up -d

# Access Grafana
open http://your-domain.com:3001
# Login: admin/admin (change on first login)

# Import dashboards
# Go to Dashboards > Import > Upload JSON
# Use files in infrastructure/monitoring/grafana/dashboards/
```

### Alerting

```bash
# Configure Alertmanager
nano infrastructure/monitoring/alertmanager.yml

# Update:
# - Email settings
# - Slack webhook
# - PagerDuty key

# Restart alertmanager
docker-compose restart alertmanager
```

---

## 💾 Backup Configuration

### Database Backups

#### Automated Backups
```bash
# Setup cron job
crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/smart-news-aggregator/scripts/backup_db.sh

# Weekly backup at Sunday 3 AM
0 3 * * 0 /path/to/smart-news-aggregator/scripts/backup_db.sh
```

#### Manual Backup
```bash
# Run backup script
bash scripts/backup_db.sh

# Backups stored in ./backups/
```

### Volume Backups
```bash
# Backup Docker volumes
docker run --rm -v smart-news_postgres_data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/postgres_data.tar.gz /data

docker run --rm -v smart-news_redis_data:/data -v $(pwd)/backups:/backup \
  alpine tar czf /backup/redis_data.tar.gz /data
```

---

## 🔄 Updates & Rollback

### Rolling Update (Zero Downtime)

#### Docker Compose
```bash
# Pull latest images
docker-compose -f docker-compose.prod.yml pull

# Update services one by one
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
docker-compose -f docker-compose.prod.yml up -d --no-deps ml_service
docker-compose -f docker-compose.prod.yml up -d --no-deps scraper

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

#### Kubernetes
```bash
# Update image
kubectl set image deployment/backend backend=registry.example.com/smart-news/backend:v1.1.0 -n smart-news

# Watch rollout
kubectl rollout status deployment/backend -n smart-news
```

### Rollback

#### Docker Compose
```bash
# Rollback to previous version
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# Restore database if needed
docker exec smart-news-postgres psql -U postgres -d news_aggregator < backups/latest.sql
```

#### Kubernetes
```bash
# Rollback deployment
kubectl rollout undo deployment/backend -n smart-news

# Check rollout history
kubectl rollout history deployment/backend -n smart-news
```

---

## 📈 Scaling

### Horizontal Scaling

#### Docker Compose
```bash
# Scale specific service
docker-compose -f docker-compose.prod.yml up -d --scale backend=3 --scale ml_service=2
```

#### Kubernetes
```bash
# Scale deployment
kubectl scale deployment backend --replicas=5 -n smart-news
kubectl scale deployment ml-service --replicas=3 -n smart-news
kubectl scale deployment scraper-worker --replicas=10 -n smart-news

# Auto-scaling
kubectl autoscale deployment backend --cpu-percent=70 --min=2 --max=10 -n smart-news
```

### Database Scaling

#### Read Replicas
```yaml
# docker-compose.prod.yml
postgres-replica:
  image: postgres:15
  environment:
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  command: postgres -c 'hot_standby=on'
```

#### Redis Cluster
```bash
# Setup Redis cluster
docker-compose -f infrastructure/redis-cluster/docker-compose.yml up -d
```

---

## 🔍 Monitoring & Logs

### View Logs

#### Docker Compose
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f ml_service
```

#### Kubernetes
```bash
# Pod logs
kubectl logs -f deployment/backend -n smart-news

# Previous logs
kubectl logs --previous deployment/backend -n smart-news

# Stream logs
kubectl logs -f -l app=backend -n smart-news
```

### Centralized Logging

#### ELK Stack
```bash
# Start ELK stack
docker-compose -f infrastructure/elk/docker-compose.yml up -d

# Access Kibana
open http://your-domain.com:5601
```

---

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
docker-compose logs backend

# Check container status
docker-compose ps

# Restart service
docker-compose restart backend
```

### Database Connection Issues
```bash
# Check PostgreSQL
docker exec smart-news-postgres pg_isready

# Check connections
docker exec smart-news-postgres psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Reset connections
docker-compose restart postgres
```

### High Memory Usage
```bash
# Check memory usage
docker stats

# Check specific container
docker stats smart-news-backend

# Restart services
docker-compose restart
```

### Disk Space Issues
```bash
# Check disk space
df -h

# Clean Docker
docker system prune -a --volumes

# Clean old images
docker image prune -a
```

---

## 📞 Support & Maintenance

### Health Checks
```bash
# Automated health check
bash scripts/check_services.sh

# Manual checks
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Performance Monitoring
```bash
# Backend metrics
curl http://localhost:8000/metrics

# ML service metrics
curl http://localhost:8001/metrics
```

---

## 🎯 Production Best Practices

1. **Use environment-specific configs**
   - Separate dev/staging/prod configs
   - Use secrets management
   - Never commit secrets to git

2. **Enable monitoring**
   - Setup Prometheus + Grafana
   - Configure alerts
   - Monitor all services

3. **Setup backups**
   - Daily database backups
   - Backup retention policy
   - Test restore procedure

4. **Security**
   - Use HTTPS only
   - Enable rate limiting
   - Regular security updates
   - Firewall configuration

5. **High Availability**
   - Multiple replicas
   - Load balancing
   - Database replication
   - Automated failover

6. **Documentation**
   - Keep runbooks updated
   - Document procedures
   - Incident response plan

---

## 📚 Additional Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [API Documentation](API.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Last Updated:** October 2025  
**Version:** 1.0.0
