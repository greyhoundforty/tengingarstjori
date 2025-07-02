#!/bin/bash
# Quick reset script for Tengingarstjóri testing
# This script completely resets the tg state so you can test init repeatedly

echo "🧹 Resetting Tengingarstjóri state..."

# Remove all tg files
rm -rf ~/.tengingarstjori
rm -f ~/.ssh/config.tengingarstjori
rm -f ~/.ssh/config.backup
rm -f ~/.ssh/config.tengingarstjori-backup

# Clean SSH config (cross-platform)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' '/Include.*config\.tengingarstjori/d' ~/.ssh/config 2>/dev/null || true
else
    # Linux
    sed -i '/Include.*config\.tengingarstjori/d' ~/.ssh/config 2>/dev/null || true
fi

echo "✅ Reset complete! You can now run 'tg init' again."
echo ""
echo "Current state:"
echo "  Configuration dir: $([ -d ~/.tengingarstjori ] && echo 'EXISTS' || echo 'REMOVED')"
echo "  Managed config: $([ -f ~/.ssh/config.tengingarstjori ] && echo 'EXISTS' || echo 'REMOVED')"
echo "  Backup file: $([ -f ~/.ssh/config.backup ] && echo 'EXISTS' || echo 'REMOVED')"
