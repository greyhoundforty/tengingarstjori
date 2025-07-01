#!/bin/bash
# Quick test script to check our coverage improvements

set -e

echo "🧪 Testing coverage improvements..."

# Run tests with coverage
python -m pytest tests/ -v --tb=short --cov=src --cov-report=term --cov-report=html --cov-fail-under=50

echo ""
echo "📊 Coverage report:"
echo "  - Terminal: shown above"
echo "  - HTML: htmlcov/index.html"
echo ""
echo "✅ Test complete!"
