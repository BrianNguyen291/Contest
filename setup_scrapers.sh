#!/bin/bash
# AA.com Scraper Setup Script
# This script installs the necessary dependencies for scraping AA.com

echo "🛫 AA.com Scraper Setup"
echo "======================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found: $(pip3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing scraping dependencies..."
pip install -r scraper_requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Available scrapers:"
echo "  1. Scrapling scraper: python3 aa_scraper_scrapling.py"
echo "  2. Crawlee scraper: python3 aa_scraper_crawlee.py"
echo ""
echo "💡 To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "⚠️  Note: The scrapers will open a browser window by default."
echo "   Set headless=True in the scripts for production use."
