#!/bin/bash

# Smart News Aggregator - Quick Start Script

set -e

echo "🚀 Smart News Aggregator - Starting..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "🐳 Starting Docker containers..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📚 Available endpoints:"
echo "  - API: http://localhost:8000"
echo "  - Swagger Docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"
echo "  - RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: docker-compose logs -f backend"
echo "  - Stop services: docker-compose down"
echo "  - Restart: docker-compose restart"
echo ""
echo "🎉 Happy coding!"
