#!/bin/bash

# Space Shooter Game Launcher Script
echo "🚀 Starting Space Shooter Game..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import pygame, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📥 Installing required packages..."
    pip3 install -r requirements.txt
fi

echo "🎮 Launching game..."
python3 space_shooter_final.py

echo "👋 Thanks for playing!"
