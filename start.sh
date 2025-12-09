#!/bin/bash

# ETL Service Startup Script

echo "🚀 Starting ETL Service..."

# Check if .env file exists, if not create from template
if [ ! -f .env ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. You may want to customize the settings."
fi

# Start all services
echo "🐳 Starting Docker services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🏥 Checking service health..."
curl -f http://localhost:8000/api/v1/health || echo "❌ Backend health check failed"

echo ""
echo "🎉 ETL Service is starting up!"
echo ""
echo "📊 Access URLs:"
echo "   • Frontend UI:      http://localhost:3000"
echo "   • Backend API:      http://localhost:8000"
echo "   • API Docs:         http://localhost:8000/docs"
echo "   • RabbitMQ UI:      http://localhost:15672 (admin/password)"
echo ""
echo "🔧 Management Commands:"
echo "   • View logs:        docker-compose logs -f"
echo "   • Stop services:    docker-compose down"
echo "   • Rebuild:          docker-compose build"
echo ""

# Show running containers
echo "📦 Running containers:"
docker-compose ps