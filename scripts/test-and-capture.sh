#!/bin/bash
# Quick test runner that saves results

set -e

echo "🧪 Running tests and saving results..."

# Run tests and save to file
python -m pytest tests/ -v --tb=short --cov=src --cov-report=term-missing --cov-fail-under=60 2>&1 | tee test_results.log

echo ""
echo "📝 Test results saved to test_results.log"
echo "📊 You can now share this file for analysis"

# Also run a quick lint check
echo ""
echo "🔍 Running quick lint check..."
python -m flake8 src/ tests/ 2>&1 | tee lint_results.log || echo "Linting issues found - see lint_results.log"

echo ""
echo "✅ Test and lint results captured!"
echo "Files created:"
echo "  - test_results.log (test output)"
echo "  - lint_results.log (linting output)"
