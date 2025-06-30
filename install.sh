#!/bin/bash
set -e

echo "🚀 Installing Tengingarstjóri SSH Connection Manager..."

# Check if Python 3.10+ is available
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.10+ required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Install the package
echo "📦 Installing tengingarstjori..."
pip install -e .

# Check if installation worked
echo "🔧 Testing installation..."
if command -v tg &> /dev/null; then
    echo "✅ 'tg' command is now available!"
    echo ""
    echo "🎉 Installation complete!"
    echo ""
    echo "Next steps:"
    echo "1. Run 'tg init' to set up SSH integration"
    echo "2. Add connections with 'tg add'"
    echo "3. List connections with 'tg list'"
    echo ""
    echo "Get help: tg --help"
else
    echo "❌ Installation failed. The 'tg' command is not available."
    echo "Check your Python PATH configuration."
    exit 1
fi
