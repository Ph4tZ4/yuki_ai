#!/bin/bash

# Yuki AI Installation Script for macOS
# This script will install all necessary dependencies and set up Yuki AI

echo "🎤 Installing Yuki AI - Thai Voice Assistant"
echo "=============================================="

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 1 ]]; then
    echo "✅ Python $python_version found"
else
    echo "❌ Python 3.8+ is required. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Homebrew is installed
if command -v brew &> /dev/null; then
    echo "✅ Homebrew found"
else
    echo "❌ Homebrew is required. Please install Homebrew first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
brew install portaudio

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Make run script executable
chmod +x run.py

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "To start Yuki AI:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python run.py"
echo ""
echo "Or use the launcher script: ./run.py"
echo ""
echo "Make sure to grant microphone permissions when prompted!"
