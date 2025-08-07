#!/bin/bash
"""
FortiGate API Client - One-Click Installation Script

This script sets up the complete FortiGate API Client with AI/ML capabilities.
"""

set -e  # Exit on any error

echo "🚀 FortiGate API Client - Installation Script"
echo "=============================================="

# Check Python version
echo "🐍 Checking Python version..."
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "✅ Python $PYTHON_VERSION is compatible"
else
    echo "❌ Python 3.8+ required, found $PYTHON_VERSION"
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check if virtual environment exists
if [[ ! -d ".venv" ]]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Run ML setup verification
echo "🤖 Verifying ML/AI setup..."
python3 setup_ml.py

# Make executable script executable
chmod +x fgt

# Create initial config if it doesn't exist
if [[ ! -f "config.ini" ]]; then
    echo "⚙️  Creating initial configuration..."
    cp config.ini.example config.ini
    echo "📝 Please edit config.ini with your FortiGate details"
fi

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Edit config.ini with your FortiGate IP and API key"
echo "2. Test the installation:"
echo "   ./fgt --ai-status -c config.ini"
echo "3. Try a natural language query:"
echo "   ./fgt --enable-ai --ai-query 'show system status' -c config.ini -m get -e /cmdb/system/status"
echo "4. Start interactive mode:"
echo "   ./fgt --interactive -c config.ini"
echo ""
echo "📖 See README.md for complete documentation"
echo "🤖 Run 'python3 ml_demo.py' to see AI capabilities"
