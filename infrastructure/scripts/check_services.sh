#!/bin/bash

# Health check script for Smart News Aggregator
# Checks all services and their connectivity

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Smart News Aggregator Health Check  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    printf "%-20s" "$name:"
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null); then
        if [ "$response" -eq "$expected_code" ]; then
            echo -e "${GREEN}✓ Healthy (HTTP $response)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ Warning (HTTP $response)${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Down or unreachable${NC}"
        return 1
    fi
}

# Function to check Docker container
check_container() {
    local name=$1
    local container=$2
    
    printf "%-20s" "$name:"
    
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null)
        if [ "$status" = "running" ]; then
            echo -e "${GREEN}✓ Running${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠ Status: $status${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Not found${NC}"
        return 1
    fi
}

# Check Docker containers
echo -e "${BLUE}Docker Containers:${NC}"
check_container "Backend" "smart-news-backend"
check_container "ML Service" "smart-news-ml-service"
check_container "Scraper" "smart-news-scraper"
check_container "Frontend" "smart-news-frontend"
check_container "PostgreSQL" "smart-news-postgres"
check_container "Redis" "smart-news-redis"
check_container "RabbitMQ" "smart-news-rabbitmq"
check_container "Elasticsearch" "smart-news-elasticsearch"
echo ""

# Check HTTP endpoints
echo -e "${BLUE}HTTP Endpoints:${NC}"
check_service "Backend API" "http://localhost:8000/health"
check_service "ML Service" "http://localhost:8001/health"
check_service "Frontend" "http://localhost:3000"
check_service "Flower" "http://localhost:5555"
check_service "RabbitMQ" "http://localhost:15672"
echo ""

# Check database connectivity
echo -e "${BLUE}Database Connectivity:${NC}"
printf "%-20s" "PostgreSQL:"
if docker exec smart-news-postgres pg_isready -q 2>/dev/null; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${RED}✗ Cannot connect${NC}"
fi

printf "%-20s" "Redis:"
if docker exec smart-news-redis redis-cli ping 2>/dev/null | grep -q PONG; then
    echo -e "${GREEN}✓ Connected${NC}"
else
    echo -e "${RED}✗ Cannot connect${NC}"
fi
echo ""

# Check disk space
echo -e "${BLUE}System Resources:${NC}"
printf "%-20s" "Disk Space:"
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    echo -e "${GREEN}✓ ${disk_usage}% used${NC}"
elif [ "$disk_usage" -lt 90 ]; then
    echo -e "${YELLOW}⚠ ${disk_usage}% used${NC}"
else
    echo -e "${RED}✗ ${disk_usage}% used (Critical)${NC}"
fi

# Check memory
printf "%-20s" "Memory:"
mem_usage=$(free | awk 'NR==2 {printf "%.0f", $3/$2*100}')
if [ "$mem_usage" -lt 80 ]; then
    echo -e "${GREEN}✓ ${mem_usage}% used${NC}"
elif [ "$mem_usage" -lt 90 ]; then
    echo -e "${YELLOW}⚠ ${mem_usage}% used${NC}"
else
    echo -e "${RED}✗ ${mem_usage}% used (High)${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Health Check Complete        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}✓${NC} = Healthy  ${YELLOW}⚠${NC} = Warning  ${RED}✗${NC} = Down"
echo ""
