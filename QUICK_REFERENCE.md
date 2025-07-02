# Tengingarstjóri Quick Reference Guide

## Enhanced List Command

### Basic Usage
```bash
tg list                    # Standard table view
tg list --detailed         # Show all details (notes, proxy, forwarding)
tg list -d                 # Short form for detailed
tg list --format compact   # Compact space-efficient format
tg list -f compact         # Short form for compact format
tg list -d -f compact      # Detailed + compact (best for many connections)
```

### What the Detailed View Shows
- **Connection info**: user@host:port with SSH hostname if different
- **SSH Key**: Key filename if specified
- **ProxyJump**: Jump server configuration with color coding
- **Port Forwarding**: Local and remote forwarding rules
- **Notes**: Connection descriptions and reminders
- **Last Used**: When the connection was last accessed

## Adding Connections with Advanced Features

### Basic Connection
```bash
tg add -n "server1" -h "192.168.1.10" -u "admin"
```

### ProxyJump Examples
```bash
# Simple jump through bastion
tg add -n "internal" -h "10.0.1.100" -u "admin" --proxy-jump "bastion.company.com"

# Jump with specific user and port
tg add -n "db-server" -h "192.168.10.50" -u "dbadmin" --proxy-jump "jumpuser@bastion.company.com:2222"

# Multi-hop (through multiple servers)
tg add -n "deep-internal" -h "172.16.5.10" -u "root" --proxy-jump "jump1.com,user@jump2.com"
```

### Port Forwarding Examples
```bash
# Local forwarding (remote service -> local port)
tg add -n "db-tunnel" -h "db.company.com" -u "dbuser" --local-forward "3306:localhost:3306"

# Multiple local forwards
tg add -n "dev-stack" -h "dev.company.com" -u "dev" --local-forward "8080:localhost:80,3306:db:3306"

# Remote forwarding (local service -> remote port)
tg add -n "demo-server" -h "demo.company.com" -u "demo" --remote-forward "8080:localhost:3000"

# SOCKS proxy
tg add -n "proxy" -h "proxy.company.com" -u "user" --local-forward "1080"
```

### Complete Example
```bash
tg add -n "prod-db" \
    --host "prod-db.internal" \
    --user "produser" \
    --proxy-jump "bastion.company.com" \
    --local-forward "5432:localhost:5432" \
    --key "~/.ssh/prod_key" \
    --notes "Production PostgreSQL via bastion"
```

## Quick Testing

### Test the Features
```bash
# Run the feature demonstration
chmod +x test_features.sh
./test_features.sh

# Reset for clean testing
./reset_tg.sh
```

### Verify Connections
```bash
# Check what was generated
tg list -d                              # See all connections with details
tg show connection-name                 # Individual connection details
cat ~/.ssh/config.tengingarstjori       # See generated SSH config
ssh connection-name                     # Test the actual connection
```

## Ready to Test!

You now have:

1. **Enhanced list command** with `--detailed` and `--format` options
2. **Comprehensive examples** for ProxyJump and port forwarding
3. **Test scripts** to try everything out
4. **Quick reference** for syntax and patterns

### Start Testing
```bash
# Make scripts executable
chmod +x test_features.sh reset_tg.sh

# Run the demonstration
./test_features.sh

# Or test manually
./reset_tg.sh
tg init
tg add -n "test-server" -h "example.com" -u "user" --proxy-jump "bastion.example.com" --notes "Test connection"
tg list --detailed
```
