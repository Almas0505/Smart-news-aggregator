# Makefile for Smart News Aggregator

.PHONY: help build up down restart logs clean test lint format

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Smart News Aggregator - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ==================== Docker Commands ====================

build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build

up: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started!$(NC)"
	@make status

down: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker-compose down
	@echo "$(YELLOW)✓ Services stopped$(NC)"

restart: ## Restart all services
	@echo "$(YELLOW)Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

logs: ## View logs from all services
	docker-compose logs -f

logs-backend: ## View backend logs
	docker-compose logs -f backend

logs-ml: ## View ML service logs
	docker-compose logs -f ml_service

logs-scraper: ## View scraper logs
	docker-compose logs -f scraper

logs-frontend: ## View frontend logs
	docker-compose logs -f frontend

status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker-compose ps

# ==================== Database Commands ====================

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	docker-compose exec backend alembic upgrade head
	@echo "$(GREEN)✓ Migrations completed$(NC)"

db-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back migration...$(NC)"
	docker-compose exec backend alembic downgrade -1

db-seed: ## Seed database with test data
	@echo "$(BLUE)Seeding database...$(NC)"
	docker-compose exec backend python scripts/seed_data.py
	@echo "$(GREEN)✓ Database seeded$(NC)"

db-shell: ## Open PostgreSQL shell
	docker exec -it smart-news-postgres psql -U postgres -d news_aggregator

db-backup: ## Backup database
	@echo "$(BLUE)Creating database backup...$(NC)"
	bash scripts/backup_db.sh

redis-shell: ## Open Redis shell
	docker exec -it smart-news-redis redis-cli

# ==================== Development Commands ====================

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload

dev-ml: ## Run ML service in development mode
	cd ml_service && uvicorn app.main:app --port 8001 --reload

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

dev-scraper: ## Run scraper worker
	cd scraper_service && celery -A app.celery_app worker --loglevel=info

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@echo "Backend..."
	cd backend && pip install -r requirements.txt
	@echo "ML Service..."
	cd ml_service && pip install -r requirements.txt
	@echo "Scraper..."
	cd scraper_service && pip install -r requirements.txt
	@echo "Frontend..."
	cd frontend && npm install
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

# ==================== Testing Commands ====================

test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	docker-compose exec backend pytest
	@echo "$(GREEN)✓ Tests completed$(NC)"

test-backend: ## Run backend tests
	cd backend && pytest -v

test-coverage: ## Run tests with coverage
	cd backend && pytest --cov=app --cov-report=html
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-integration: ## Run integration tests
	cd backend && pytest tests/integration/

# ==================== Code Quality Commands ====================

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	cd backend && flake8 app/
	cd ml_service && flake8 app/
	cd scraper_service && flake8 app/
	@echo "$(GREEN)✓ Linting completed$(NC)"

format: ## Format code with Black
	@echo "$(BLUE)Formatting code...$(NC)"
	cd backend && black app/
	cd ml_service && black app/
	cd scraper_service && black app/
	@echo "$(GREEN)✓ Code formatted$(NC)"

type-check: ## Run type checking
	@echo "$(BLUE)Type checking...$(NC)"
	cd backend && mypy app/
	@echo "$(GREEN)✓ Type checking completed$(NC)"

# ==================== Scraping Commands ====================

scrape: ## Trigger manual scraping
	@echo "$(BLUE)Triggering news scraping...$(NC)"
	curl -X POST http://localhost:8000/api/v1/admin/scrape/trigger
	@echo ""
	@echo "$(GREEN)✓ Scraping started. Check Flower at http://localhost:5555$(NC)"

flower: ## Open Flower monitoring
	@echo "$(BLUE)Opening Flower...$(NC)"
	open http://localhost:5555 || xdg-open http://localhost:5555

# ==================== Monitoring Commands ====================

prometheus: ## Open Prometheus
	@echo "$(BLUE)Opening Prometheus...$(NC)"
	open http://localhost:9090 || xdg-open http://localhost:9090

grafana: ## Open Grafana
	@echo "$(BLUE)Opening Grafana (admin/admin)...$(NC)"
	open http://localhost:3001 || xdg-open http://localhost:3001

rabbitmq: ## Open RabbitMQ management
	@echo "$(BLUE)Opening RabbitMQ (guest/guest)...$(NC)"
	open http://localhost:15672 || xdg-open http://localhost:15672

# ==================== Cleanup Commands ====================

clean: ## Remove all containers, volumes, and generated files
	@echo "$(RED)⚠️  This will remove all containers and volumes!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true; \
		find . -type f -name "*.pyc" -delete 2>/dev/null || true; \
		find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true; \
		rm -rf backend/htmlcov 2>/dev/null || true; \
		rm -rf frontend/.next 2>/dev/null || true; \
		rm -rf frontend/node_modules 2>/dev/null || true; \
		echo "$(GREEN)✓ Cleanup completed$(NC)"; \
	fi

clean-cache: ## Clean Python cache files
	@echo "$(BLUE)Cleaning cache...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cache cleaned$(NC)"

# ==================== Health Check Commands ====================

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@bash scripts/check_services.sh

check: ## Quick service check
	@echo "Backend:    $(shell curl -s http://localhost:8000/health 2>/dev/null || echo '❌')"
	@echo "ML Service: $(shell curl -s http://localhost:8001/health 2>/dev/null || echo '❌')"
	@echo "Frontend:   $(shell curl -s http://localhost:3000 >/dev/null 2>&1 && echo '✅' || echo '❌')"
	@echo "Flower:     $(shell curl -s http://localhost:5555 >/dev/null 2>&1 && echo '✅' || echo '❌')"

# ==================== Deployment Commands ====================

deploy-dev: ## Deploy to development environment
	@echo "$(BLUE)Deploying to development...$(NC)"
	docker-compose -f docker-compose.yml up -d --build
	@echo "$(GREEN)✓ Deployed to development$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d --build
	@echo "$(GREEN)✓ Deployed to production$(NC)"

# ==================== Quick Start Commands ====================

quickstart: build up db-migrate db-seed ## Quick start (build, start, migrate, seed)
	@echo ""
	@echo "$(GREEN)🎉 Smart News Aggregator is ready!$(NC)"
	@echo ""
	@echo "$(BLUE)Available URLs:$(NC)"
	@echo "  Frontend:   http://localhost:3000"
	@echo "  Backend:    http://localhost:8000/docs"
	@echo "  ML Service: http://localhost:8001/docs"
	@echo "  Flower:     http://localhost:5555"
	@echo "  RabbitMQ:   http://localhost:15672 (guest/guest)"
	@echo "  Grafana:    http://localhost:3001 (admin/admin)"
	@echo ""

# ==================== Info Commands ====================

info: ## Show project information
	@echo "$(BLUE)═══════════════════════════════════════════$(NC)"
	@echo "$(BLUE)   Smart News Aggregator - Project Info$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(GREEN)Services:$(NC)"
	@echo "  • Backend API (FastAPI)"
	@echo "  • ML Service (AI/ML)"
	@echo "  • Scraper Service (Celery)"
	@echo "  • Frontend (Next.js)"
	@echo ""
	@echo "$(GREEN)Databases:$(NC)"
	@echo "  • PostgreSQL (Main DB)"
	@echo "  • Redis (Cache)"
	@echo "  • Elasticsearch (Search)"
	@echo "  • RabbitMQ (Queue)"
	@echo ""
	@echo "$(GREEN)Quick Commands:$(NC)"
	@echo "  make quickstart  - Full setup"
	@echo "  make up          - Start services"
	@echo "  make down        - Stop services"
	@echo "  make logs        - View logs"
	@echo "  make health      - Check health"
	@echo ""
	@echo "$(BLUE)For more commands: make help$(NC)"
	@echo ""

version: ## Show versions of key components
	@echo "$(BLUE)Component Versions:$(NC)"
	@echo "Python:        $(shell python --version 2>&1)"
	@echo "Node.js:       $(shell node --version 2>&1)"
	@echo "Docker:        $(shell docker --version 2>&1)"
	@echo "Docker Compose:$(shell docker-compose --version 2>&1)"

.DEFAULT_GOAL := help
