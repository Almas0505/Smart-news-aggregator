#!/bin/bash

# Database backup script for Smart News Aggregator

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="news_aggregator_${TIMESTAMP}.sql"
CONTAINER_NAME="smart-news-postgres"
DB_NAME="news_aggregator"
DB_USER="postgres"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PostgreSQL Backup Script            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}📦 Creating backup...${NC}"
echo -e "   Database: $DB_NAME"
echo -e "   File: $BACKUP_FILE"
echo ""

# Create backup
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    # Compress backup
    echo -e "${BLUE}🗜️  Compressing backup...${NC}"
    gzip "$BACKUP_DIR/$BACKUP_FILE"
    
    COMPRESSED_FILE="${BACKUP_FILE}.gz"
    SIZE=$(du -h "$BACKUP_DIR/$COMPRESSED_FILE" | cut -f1)
    
    echo ""
    echo -e "${GREEN}✓ Backup completed successfully!${NC}"
    echo -e "  Location: $BACKUP_DIR/$COMPRESSED_FILE"
    echo -e "  Size: $SIZE"
    echo ""
    
    # Keep only last 7 backups
    echo -e "${BLUE}🧹 Cleaning old backups (keeping last 7)...${NC}"
    ls -t "$BACKUP_DIR"/*.sql.gz 2>/dev/null | tail -n +8 | xargs -r rm --
    echo -e "${GREEN}✓ Cleanup complete${NC}"
    echo ""
    
    # List all backups
    echo -e "${BLUE}📋 Available backups:${NC}"
    ls -lh "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "   No backups found"
    echo ""
else
    echo -e "${RED}✗ Backup failed!${NC}"
    rm -f "$BACKUP_DIR/$BACKUP_FILE"
    exit 1
fi
