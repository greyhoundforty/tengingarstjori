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

# Ensure we are working inside a virtual environment to avoid polluting the
# system or mise-managed Python and prevent PATH ambiguity with the 'tg' script.
if [ -z "$VIRTUAL_ENV" ]; then
    echo ""
    echo "⚠️  No active virtual environment detected."
    echo "   It is strongly recommended to install inside a virtual environment:"
    echo ""
    echo "     python3 -m venv .venv"
    echo "     source .venv/bin/activate"
    echo "     bash install.sh"
    echo ""
    read -r -p "Continue without a virtual environment? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted. Please activate a virtual environment and re-run."
        exit 1
    fi
fi

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
    echo "   If you installed inside a virtual environment, make sure it is activated."
    echo "   You can also run the CLI directly with: python -m tengingarstjori"
    exit 1
fi
