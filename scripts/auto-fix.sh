#!/bin/bash
# Auto-fix code quality issues

set -e

echo "🔧 Auto-fixing code quality issues..."

# Format with Black
echo "📝 Running Black formatter..."
python -m black src/ tests/

# Sort imports with isort
echo "🔄 Sorting imports with isort..."
python -m isort src/ tests/

# Run autoflake to remove unused imports (if available)
if command -v autoflake &> /dev/null; then
    echo "🧹 Removing unused imports..."
    autoflake --remove-all-unused-imports --recursive --in-place src/ tests/
else
    echo "⚠️ autoflake not installed, skipping unused import removal"
    echo "   Install with: pip install autoflake"
fi

echo "✅ Auto-fix complete!"
echo ""
echo "Next steps:"
echo "1. Review the changes: git diff"
echo "2. Run tests: mise run test"
echo "3. Check quality: mise run lint"
