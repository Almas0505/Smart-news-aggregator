#!/bin/bash

# Database initialization script for Smart News Aggregator

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Database Initialization Script      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL...${NC}"
until docker exec smart-news-postgres pg_isready -q; do
    sleep 1
done
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
echo ""

# Run migrations
echo -e "${BLUE}🔄 Running database migrations...${NC}"
docker-compose exec -T backend alembic upgrade head
echo -e "${GREEN}✓ Migrations completed${NC}"
echo ""

# Seed database
echo -e "${BLUE}🌱 Seeding database...${NC}"
docker-compose exec -T backend python scripts/seed_data.py
echo -e "${GREEN}✓ Database seeded${NC}"
echo ""

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   ✓ Database initialized successfully ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
