#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting StocksPredictor AI Setup..."

# 1. Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating Virtual Environment..."
    python3 -m venv venv
fi

# 2. Activate venv
source venv/bin/activate

# 3. Upgrade pip and install requirements
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Handle Ollama Models
echo "🧠 Checking Ollama Models..."
# Check if ollama is installed
if ! command -v ollama &> /dev/null
then
    echo "⚠️ Ollama not found. Please install it from https://ollama.com"
else
    echo "📥 Pulling Llama 3.1 (Brain)..."
    ollama pull llama3.1
    echo "📥 Pulling mxbai-embed-large (Memory)..."
    ollama pull mxbai-embed-large
fi

# 5. Create necessary folders
mkdir -p db
mkdir -p reports
mkdir -p coding

echo "✅ Setup Complete! Run 'python main.py' to start the app."