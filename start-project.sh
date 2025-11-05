#!/bin/bash

# Smart News Aggregator - Full Project Startup Script
# Author: AI Assistant
# Date: October 20, 2025

set -e

echo "🚀 Starting Smart News Aggregator..."
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Stop existing containers
echo -e "\n${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Remove old volumes (optional - comment if you want to keep data)
# echo -e "\n${YELLOW}🗑️  Removing old volumes...${NC}"
# docker-compose down -v 2>/dev/null || true

# Build images
echo -e "\n${YELLOW}🔨 Building Docker images...${NC}"
docker-compose build

# Start core services first (postgres, redis, elasticsearch)
echo -e "\n${YELLOW}📦 Starting core services (Postgres, Redis, Elasticsearch)...${NC}"
docker-compose up -d postgres redis elasticsearch

# Wait for services to be healthy
echo -e "\n${YELLOW}⏳ Waiting for services to be healthy...${NC}"
echo "This may take 30-60 seconds..."

# Wait for postgres
echo -n "Waiting for Postgres"
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e " ${GREEN}✅${NC}"

# Wait for redis
echo -n "Waiting for Redis"
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e " ${GREEN}✅${NC}"

# Wait for elasticsearch
echo -n "Waiting for Elasticsearch"
until curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; do
    echo -n "."
    sleep 3
done
echo -e " ${GREEN}✅${NC}"

# Start backend service
echo -e "\n${YELLOW}🐍 Starting Backend service...${NC}"
docker-compose up -d backend

# Wait for backend
echo -n "Waiting for Backend API"
sleep 10
until curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e " ${GREEN}✅${NC}"

# Run database migrations
echo -e "\n${YELLOW}🗄️  Running database migrations...${NC}"
docker-compose exec -T backend alembic upgrade head || echo "Migrations may already be applied"

# Start ML service
echo -e "\n${YELLOW}🤖 Starting ML service...${NC}"
docker-compose up -d ml_service

# Start scraper worker
echo -e "\n${YELLOW}🕷️  Starting Scraper worker...${NC}"
docker-compose up -d scraper_worker

# Start monitoring services
echo -e "\n${YELLOW}📊 Starting Monitoring services (Prometheus, Grafana, Flower)...${NC}"
docker-compose up -d prometheus grafana flower node-exporter redis-exporter postgres-exporter

# Start frontend
echo -e "\n${YELLOW}🎨 Starting Frontend...${NC}"
docker-compose up -d frontend

# Start nginx
echo -e "\n${YELLOW}🌐 Starting Nginx reverse proxy...${NC}"
docker-compose up -d nginx

# Show status
echo -e "\n${GREEN}=================================="
echo "✅ All services started successfully!"
echo "==================================${NC}\n"

# Display service URLs
echo -e "${GREEN}📋 Service URLs:${NC}"
echo "-----------------------------------"
echo "🌐 Frontend:        http://localhost:3001"
echo "🔌 Backend API:     http://localhost:8000"
echo "📖 API Docs:        http://localhost:8000/docs"
echo "🤖 ML Service:      http://localhost:8001"
echo "🕷️  Flower (Tasks):  http://localhost:5555"
echo "📊 Prometheus:      http://localhost:9090"
echo "📈 Grafana:         http://localhost:3000 (admin/admin)"
echo "🔍 Elasticsearch:   http://localhost:9200"
echo "-----------------------------------"

# Display logs commands
echo -e "\n${YELLOW}📝 Useful commands:${NC}"
echo "View all logs:      docker-compose logs -f"
echo "View backend logs:  docker-compose logs -f backend"
echo "Stop all services:  docker-compose down"
echo "Restart service:    docker-compose restart <service_name>"
echo "Show containers:    docker-compose ps"

# Check if services are running
echo -e "\n${YELLOW}🔍 Checking service status...${NC}"
docker-compose ps

echo -e "\n${GREEN}🎉 Project is ready!${NC}"
echo -e "You can now test the fresh news API:"
echo -e "${YELLOW}curl http://localhost:8000/api/v1/news/fresh${NC}\n"
