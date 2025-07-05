#!/bin/bash

# News Bot Startup Script
# This script handles the startup of the news bot with proper error handling

echo "🤖 Starting News Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found! Please copy .env.example to .env and configure it."
    echo "cp .env.example .env"
    exit 1
fi

# Create logs directory
mkdir -p logs

# Check if database exists, if not create it
if [ ! -f "bot_data.db" ]; then
    echo "🗄️ Database not found, it will be created automatically."
fi

# Start the bot
echo "🚀 Starting bot..."
python main.py

# If bot exits, show message
echo "⏹️ Bot stopped."