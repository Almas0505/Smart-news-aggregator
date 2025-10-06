#!/bin/bash

# Deployment script for Smart News Aggregator
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
ENVIRONMENT=${1:-development}
VERSION=${2:-latest}

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Smart News Aggregator Deployment     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "Environment: ${GREEN}$ENVIRONMENT${NC}"
echo -e "Version: ${GREEN}$VERSION${NC}"
echo ""

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker found${NC}"
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}✗ Docker Compose is not installed${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose found${NC}"
    
    echo ""
}

# Function to build images
build_images() {
    echo -e "${BLUE}Building Docker images...${NC}"
    
    echo "Building backend..."
    docker build -f infrastructure/docker/backend.Dockerfile -t smart-news/backend:$VERSION .
    
    echo "Building ML service..."
    docker build -f infrastructure/docker/ml.Dockerfile -t smart-news/ml-service:$VERSION .
    
    echo "Building scraper..."
    docker build -f infrastructure/docker/scraper.Dockerfile -t smart-news/scraper:$VERSION .
    
    echo "Building frontend..."
    docker build -t smart-news/frontend:$VERSION frontend/
    
    echo -e "${GREEN}✓ All images built successfully${NC}"
    echo ""
}

# Function to deploy development
deploy_development() {
    echo -e "${BLUE}Deploying to development...${NC}"
    
    # Stop existing containers
    docker-compose down
    
    # Start services
    docker-compose up -d
    
    # Wait for services
    echo "Waiting for services to start..."
    sleep 10
    
    # Run migrations
    echo "Running database migrations..."
    docker-compose exec -T backend alembic upgrade head
    
    # Seed database
    echo "Seeding database..."
    docker-compose exec -T backend python scripts/seed_data.py
    
    echo -e "${GREEN}✓ Development deployment complete${NC}"
}

# Function to deploy production
deploy_production() {
    echo -e "${BLUE}Deploying to production...${NC}"
    
    # Backup database
    echo "Creating database backup..."
    bash scripts/backup_db.sh
    
    # Pull latest images
    docker-compose -f docker-compose.prod.yml pull
    
    # Stop services gracefully
    docker-compose -f docker-compose.prod.yml down
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services
    echo "Waiting for services to start..."
    sleep 15
    
    # Run migrations
    echo "Running database migrations..."
    docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head
    
    # Health check
    echo "Performing health check..."
    bash scripts/check_services.sh
    
    echo -e "${GREEN}✓ Production deployment complete${NC}"
}

# Function to deploy to Kubernetes
deploy_kubernetes() {
    echo -e "${BLUE}Deploying to Kubernetes...${NC}"
    
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}✗ kubectl is not installed${NC}"
        exit 1
    fi
    
    # Apply Kubernetes manifests
    echo "Applying Kubernetes manifests..."
    kubectl apply -k infrastructure/kubernetes/overlays/$ENVIRONMENT
    
    # Wait for rollout
    echo "Waiting for rollout to complete..."
    kubectl rollout status deployment/backend -n smart-news
    kubectl rollout status deployment/ml-service -n smart-news
    kubectl rollout status deployment/scraper-worker -n smart-news
    kubectl rollout status deployment/frontend -n smart-news
    
    echo -e "${GREEN}✓ Kubernetes deployment complete${NC}"
}

# Function to show deployment status
show_status() {
    echo ""
    echo -e "${BLUE}Deployment Status:${NC}"
    echo ""
    
    if [ "$DEPLOY_METHOD" = "docker-compose" ]; then
        docker-compose ps
    elif [ "$DEPLOY_METHOD" = "kubernetes" ]; then
        kubectl get pods -n smart-news
    fi
    
    echo ""
    echo -e "${GREEN}Access URLs:${NC}"
    echo "  Frontend:   http://localhost:3000"
    echo "  Backend:    http://localhost:8000/docs"
    echo "  ML Service: http://localhost:8001/docs"
    echo "  Flower:     http://localhost:5555"
    echo "  RabbitMQ:   http://localhost:15672"
    echo "  Grafana:    http://localhost:3001"
    echo ""
}

# Main deployment flow
main() {
    check_prerequisites
    
    # Ask deployment method
    echo -e "${YELLOW}Select deployment method:${NC}"
    echo "1) Docker Compose (Development)"
    echo "2) Docker Compose (Production)"
    echo "3) Kubernetes"
    read -p "Enter choice [1-3]: " choice
    
    case $choice in
        1)
            DEPLOY_METHOD="docker-compose"
            build_images
            deploy_development
            ;;
        2)
            DEPLOY_METHOD="docker-compose"
            build_images
            deploy_production
            ;;
        3)
            DEPLOY_METHOD="kubernetes"
            build_images
            deploy_kubernetes
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            exit 1
            ;;
    esac
    
    show_status
    
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  Deployment completed successfully!   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
}

# Run main function
main
