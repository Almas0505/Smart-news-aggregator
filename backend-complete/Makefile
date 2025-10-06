.PHONY: help install dev up down logs clean test migrate revision init-db format lint

help:
	@echo "Smart News Aggregator - Available commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Run development server locally"
	@echo "  make up          - Start all services with Docker Compose"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - Show logs"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make test        - Run tests"
	@echo "  make migrate     - Run database migrations"
	@echo "  make revision    - Create new migration"
	@echo "  make init-db     - Initialize database with seed data"
	@echo "  make format      - Format code with black"
	@echo "  make lint        - Lint code with flake8"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f backend

clean:
	docker-compose down -v
	rm -rf __pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	pytest tests/ -v --cov=app --cov-report=html

migrate:
	alembic upgrade head

revision:
	@read -p "Enter migration message: " message; \
	alembic revision --autogenerate -m "$$message"

init-db:
	python -m app.db.init_db

format:
	black app/ tests/

lint:
	flake8 app/ tests/
	mypy app/

shell:
	docker-compose exec backend bash

db-shell:
	docker-compose exec postgres psql -U postgres -d news_aggregator
