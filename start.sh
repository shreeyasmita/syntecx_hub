#!/bin/bash

# SynTeCX Hub - Startup Script
# This script starts the complete ML house price prediction platform

set -e

echo "🚀 Starting SynTeCX House Price Prediction Platform..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/ml/models
mkdir -p backend/ml/data
mkdir -p backend/logs
mkdir -p frontend/node_modules

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."

# Check backend
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "✅ Backend API is running at http://localhost:8000"
    echo "   API Documentation: http://localhost:8000/docs"
else
    echo "⚠️  Backend API may still be starting..."
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "⚠️  Frontend may still be starting..."
fi

echo ""
echo "🎉 SynTeCX Hub Platform Started Successfully!"
echo ""
echo "Access the platform at:"
echo "  Frontend Dashboard: http://localhost:3000"
echo "  Backend API:        http://localhost:8000"
echo "  API Documentation:  http://localhost:8000/docs"
echo ""
echo "To stop the platform, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f"