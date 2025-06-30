#!/bin/bash
set -e

echo "🎨 Formatting code with Black..."

# Format all Python files
python -m black src/ tests/

echo "✅ Code formatting complete!"
