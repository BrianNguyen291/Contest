#!/bin/bash

echo "🚀 Starting AA Flight Scraper Frontend"
echo "======================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are available"

# Install dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

echo "🌐 Starting frontend development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Make sure the backend is running on port 8000"
echo ""

# Start the frontend
cd frontend
npm run dev
