# Kubernetes Deployment

Complete Kubernetes configuration for Smart News Aggregator.

## 📁 Structure

```
kubernetes/
├── base/                           # Base configurations
│   ├── namespace.yaml             # Namespace definition
│   ├── postgres-deployment.yaml   # PostgreSQL database
│   ├── redis-deployment.yaml      # Redis cache
│   ├── elasticsearch-deployment.yaml # Elasticsearch search
│   ├── backend-deployment.yaml    # FastAPI backend
│   ├── ml-service-deployment.yaml # ML service
│   ├── frontend-deployment.yaml   # Next.js frontend
│   ├── scraper-deployment.yaml    # Celery workers
│   ├── ingress.yaml              # Ingress rules
│   └── kustomization.yaml        # Kustomize config
└── overlays/
    ├── production/               # Production overrides
    │   ├── kustomization.yaml
    │   ├── backend-patch.yaml
    │   └── frontend-patch.yaml
    └── staging/                  # Staging overrides
```

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes cluster** (1.25+)
2. **kubectl** installed
3. **kustomize** installed (or use `kubectl apply -k`)
4. **Container registry** (Docker Hub, GCR, ECR, etc.)

### Step 1: Build and Push Images

```bash
# Backend
docker build -t your-registry/smart-news-backend:v1.0.0 ./backend
docker push your-registry/smart-news-backend:v1.0.0

# ML Service
docker build -t your-registry/smart-news-ml:v1.0.0 ./ml_service
docker push your-registry/smart-news-ml:v1.0.0

# Frontend
docker build -t your-registry/smart-news-frontend:v1.0.0 ./frontend
docker push your-registry/smart-news-frontend:v1.0.0

# Scraper
docker build -t your-registry/smart-news-scraper:v1.0.0 ./scraper_service
docker push your-registry/smart-news-scraper:v1.0.0
```

### Step 2: Configure Secrets

**⚠️ IMPORTANT: Change default passwords!**

```bash
# Create namespace first
kubectl apply -f base/namespace.yaml

# Create secrets
kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_PASSWORD='your-strong-password' \
  -n smart-news

kubectl create secret generic backend-secret \
  --from-literal=POSTGRES_PASSWORD='your-strong-password' \
  --from-literal=SECRET_KEY='your-secret-key-min-32-chars' \
  --from-literal=NEWS_API_KEY='your-news-api-key' \
  -n smart-news
```

### Step 3: Deploy with Kustomize

```bash
# Deploy to production
kubectl apply -k overlays/production

# Or deploy base configuration
kubectl apply -k base
```

### Step 4: Verify Deployment

```bash
# Check pods
kubectl get pods -n smart-news

# Check services
kubectl get svc -n smart-news

# Check ingress
kubectl get ingress -n smart-news

# View logs
kubectl logs -f deployment/backend -n smart-news
```

## 📊 Components

### 1. PostgreSQL Database
- **Replicas:** 1 (use StatefulSet for HA)
- **Storage:** 20Gi PVC
- **Port:** 5432
- **Resources:** 512Mi-2Gi memory, 250m-1000m CPU

### 2. Redis Cache
- **Replicas:** 1
- **Storage:** emptyDir (use PVC for persistence)
- **Port:** 6379
- **Resources:** 256Mi-512Mi memory, 100m-500m CPU

### 3. Elasticsearch
- **Replicas:** 1 (scale for production)
- **Storage:** emptyDir (use PVC)
- **Ports:** 9200 (HTTP), 9300 (transport)
- **Resources:** 2Gi-4Gi memory, 500m-2000m CPU

### 4. Backend API
- **Replicas:** 3-5 (auto-scaled)
- **Port:** 8000
- **HPA:** 2-10 pods based on CPU/memory
- **Resources:** 512Mi-1Gi memory, 250m-1000m CPU

### 5. ML Service
- **Replicas:** 2-3 (auto-scaled)
- **Port:** 8001
- **HPA:** 2-5 pods based on CPU
- **Resources:** 1Gi-2Gi memory, 500m-2000m CPU

### 6. Frontend
- **Replicas:** 2-3 (auto-scaled)
- **Port:** 3000
- **HPA:** 2-10 pods based on CPU
- **Resources:** 256Mi-512Mi memory, 100m-500m CPU

### 7. Scraper Workers
- **Replicas:** 3-5 (auto-scaled)
- **HPA:** 2-10 pods based on CPU
- **Resources:** 256Mi-512Mi memory, 100m-500m CPU

## 🔒 Security

### 1. Secrets Management

**Option A: Kubernetes Secrets**
```bash
kubectl create secret generic my-secret \
  --from-literal=key=value \
  -n smart-news
```

**Option B: Sealed Secrets** (Recommended)
```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Seal a secret
kubeseal --format yaml < secret.yaml > sealed-secret.yaml
kubectl apply -f sealed-secret.yaml
```

**Option C: External Secrets Operator**
- Integrate with AWS Secrets Manager, HashiCorp Vault, etc.

### 2. Network Policies

Create network policies to restrict pod-to-pod communication:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: smart-news
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    - podSelector:
        matchLabels:
          app: redis
```

### 3. RBAC

Limit service account permissions.

## 📈 Scaling

### Manual Scaling
```bash
# Scale backend
kubectl scale deployment backend --replicas=10 -n smart-news

# Scale ML service
kubectl scale deployment ml-service --replicas=5 -n smart-news
```

### Auto-Scaling (HPA)

Already configured for:
- **Backend:** 2-10 pods, 70% CPU, 80% memory
- **ML Service:** 2-5 pods, 75% CPU
- **Frontend:** 2-10 pods, 70% CPU
- **Scraper:** 2-10 pods, 75% CPU

### Cluster Auto-Scaler

Enable cluster autoscaling to add nodes automatically:

```bash
# For GKE
gcloud container clusters update smart-news-cluster \
  --enable-autoscaling \
  --min-nodes=3 \
  --max-nodes=20
```

## 🔍 Monitoring

### Metrics Server

Required for HPA:

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### Prometheus Operator

```bash
# Install Prometheus Operator
kubectl create -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# Create ServiceMonitor for backend
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-monitor
  namespace: smart-news
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: http
    path: /metrics
EOF
```

## 📝 Maintenance

### Database Migrations

```bash
# Run migrations as a Job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  namespace: smart-news
spec:
  template:
    spec:
      containers:
      - name: migration
        image: your-registry/smart-news-backend:v1.0.0
        command:
        - alembic
        - upgrade
        - head
        envFrom:
        - configMapRef:
            name: backend-config
        - secretRef:
            name: backend-secret
      restartPolicy: Never
  backoffLimit: 3
EOF
```

### Backup PostgreSQL

```bash
# Create backup Job
kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: smart-news
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - sh
            - -c
            - |
              pg_dump -h postgres -U postgres news_aggregator > /backup/backup-\$(date +%Y%m%d-%H%M%S).sql
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: POSTGRES_PASSWORD
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
EOF
```

## 🚨 Troubleshooting

### Pod not starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n smart-news

# Check logs
kubectl logs <pod-name> -n smart-news

# Check events
kubectl get events -n smart-news --sort-by='.lastTimestamp'
```

### Service not accessible
```bash
# Test service internally
kubectl run -it --rm debug --image=busybox --restart=Never -n smart-news -- sh
wget -O- http://backend:8000/api/v1/health

# Check endpoints
kubectl get endpoints -n smart-news
```

### Database connection issues
```bash
# Port forward to postgres
kubectl port-forward svc/postgres 5432:5432 -n smart-news

# Connect locally
psql -h localhost -U postgres -d news_aggregator
```

## 🎯 Production Checklist

- [ ] Change all default passwords
- [ ] Use proper container registry
- [ ] Configure persistent volumes
- [ ] Set up SSL/TLS (cert-manager)
- [ ] Configure monitoring (Prometheus/Grafana)
- [ ] Set up logging (ELK/Loki)
- [ ] Configure backup strategy
- [ ] Set resource limits
- [ ] Enable HPA
- [ ] Configure network policies
- [ ] Set up RBAC
- [ ] Configure ingress with rate limiting
- [ ] Test disaster recovery

## 📚 Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize](https://kustomize.io/)
- [Helm Charts](https://helm.sh/)
- [NGINX Ingress](https://kubernetes.github.io/ingress-nginx/)
- [Cert-Manager](https://cert-manager.io/)

---

**Version:** 1.0.0
**Last Updated:** November 2025
