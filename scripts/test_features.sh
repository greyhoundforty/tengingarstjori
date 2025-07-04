#!/bin/bash
# Test script for new Tengingarstjóri features
# This script demonstrates the enhanced list command and proxy/jump features

echo "🧪 Testing Enhanced Tengingarstjóri Features"
echo "==========================================="
echo ""

# Ensure we start with a clean state
echo "1. Resetting Tengingarstjóri state..."
./reset_tg.sh > /dev/null 2>&1

# Initialize
echo "2. Initializing Tengingarstjóri..."
tg init > /dev/null 2>&1

echo "3. Adding test connections with various configurations..."
echo ""

# Add basic connection
echo "   📝 Adding basic server..."
tg add -n "basic-server" -h "192.168.1.100" -u "admin" --notes "Basic server connection" --non-interactive

# Add connection with ProxyJump
echo "   📝 Adding server with ProxyJump..."
tg add -n "internal-server" -h "10.0.1.50" -u "internal" --proxy-jump "bastion.company.com" --notes "Internal server via bastion" --non-interactive

# Add connection with port forwarding
echo "   📝 Adding database tunnel..."
tg add -n "db-tunnel" -h "db.company.com" -u "dbuser" --local-forward "3306:localhost:3306" --notes "MySQL database tunnel" --non-interactive

# Add complex connection with multiple features
echo "   📝 Adding complex production setup..."
tg add -n "prod-complex" -h "prod-app.internal" -u "produser" \
    --proxy-jump "prod-bastion.company.com" \
    --local-forward "8080:localhost:80,3306:db.internal:3306" \
    --remote-forward "9000:localhost:9000" \
    --notes "Production app server with DB tunnel and reverse proxy" \
    --non-interactive

echo ""
echo "4. Demonstrating different list formats..."
echo ""

echo "📋 Basic list (default):"
echo "------------------------"
tg list
echo ""

echo "📋 Detailed table view:"
echo "----------------------"
tg list --detailed
echo ""

echo "📋 Compact format:"
echo "-----------------"
tg list --format compact
echo ""

echo "📋 Detailed compact format:"
echo "---------------------------"
tg list --detailed --format compact
echo ""

echo "5. Showing individual connection details..."
echo ""
echo "🔍 Detailed view of complex connection:"
echo "--------------------------------------"
tg show prod-complex
echo ""

echo "6. Checking generated SSH config:"
echo "--------------------------------"
if [ -f ~/.ssh/config.tengingarstjori ]; then
    echo "Generated SSH config preview:"
    head -20 ~/.ssh/config.tengingarstjori
    echo "... (truncated)"
else
    echo "❌ No managed config file found"
fi

echo ""
echo "✅ Feature demonstration complete!"
echo ""
echo "🎯 Key features demonstrated:"
echo "  • Enhanced list command with --detailed flag"
echo "  • Multiple output formats (table and compact)"
echo "  • ProxyJump configuration"
echo "  • Local and remote port forwarding"
echo "  • Complex multi-option connections"
echo "  • Generated SSH config verification"
echo ""
echo "🔧 Try these commands yourself:"
echo "  tg list -d              # Detailed view"
echo "  tg list -f compact      # Compact format"
echo "  tg list -d -f compact   # Both options"
echo "  tg show prod-complex    # Individual connection details"
echo ""
echo "📚 For more examples, see the proxy_jump_examples.sh file"
