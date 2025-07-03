# Tengingarstjóri - SSH Connection Manager

`Tengingarstjóri`, Icelandic for "Connection Manager", is a Python TUI based SSH connection manager that integrates seamlessly with your existing SSH configuration.

## Installation

### From PyPI (Recommended)

```bash
pip install tengingarstjori
```

### From Source

```bash
git clone https://github.com/yourusername/tengingarstjori.git
cd tengingarstjori
pip install -e .
```

## Features

- 🔧 **Full SSH Connection Management**: Add, remove, edit, and delete SSH connections
- 📋 **Enhanced List Views**: Detailed and compact formats with advanced option display
- 🚀 **ProxyJump Support**: Seamless bastion host and jump server configuration
- 🔀 **Port Forwarding**: Local, remote, and dynamic (SOCKS) port forwarding
- 🔑 **Smart SSH Key Management**: Automatic key discovery and defaults
- 🔗 **Non-invasive SSH Config Integration**: Preserves your existing setup
- 🎯 **Fast CLI Commands**: Intuitive `tg` prefix with rich output formatting

## Demo

<a href="https://asciinema.org/a/725744" target="_blank"><img src="https://asciinema.org/a/725744.svg" /></a>

## Quick Start

```bash
# Initialize Tengingarstjóri
tg init

# Add your first connection
tg add -n "web-server" -h "192.168.1.100" -u "admin"

# List connections
tg list

# Connect using SSH
ssh web-server
```

## Architecture

Rather than modifying your main SSH config directly, Tengingarstjóri will:

1. **Create a managed config file**: `~/.ssh/config.tengingarstjori`
2. **Add a single line to main config to include our new file**: `Include ~/.ssh/config.tengingarstjori`
3. **Manage connections separately**: All additions/changes go to the managed file
4. **Preserve your existing SSH setup**: Your existing SSH config remains untouched

## Usage Examples

### Basic Connection Management

```bash
# Add a simple connection
tg add -n "web-server" -h "192.168.1.100" -u "admin"

# Add with custom port and SSH key
tg add -n "database" -h "db.company.com" -u "dbuser" -p 2222 -k "~/.ssh/db_key"

# Interactive mode (prompts for all options)
tg add
```

### Enhanced List Views

```bash
# Standard list view
tg list

# Detailed view showing notes, proxy settings, and port forwarding
tg list --detailed
tg list -d  # Short form

# Compact format for space efficiency
tg list --format compact
tg list -f compact  # Short form

# Detailed + compact (ideal for many connections)
tg list -d -f compact

# JSON output for scripting
tg list --format json
tg list -d -f json  # Detailed JSON
```

### ProxyJump (Bastion/Jump Servers)

```bash
# Simple bastion host access
tg add -n "internal-server" -h "10.0.1.100" -u "admin" \
    --proxy-jump "bastion.company.com"

# Bastion with specific user and port
tg add -n "secure-db" -h "192.168.10.50" -u "dbadmin" \
    --proxy-jump "jumpuser@bastion.company.com:2222"

# Multi-hop through multiple servers
tg add -n "deep-internal" -h "172.16.5.10" -u "root" \
    --proxy-jump "jump1.company.com,user@jump2.internal.com"
```

### Port Forwarding

```bash
# Local port forwarding (tunnel remote service to local port)
tg add -n "mysql-tunnel" -h "db-server.company.com" -u "dbuser" \
    --local-forward "3306:localhost:3306" \
    --notes "MySQL access via localhost:3306"

# Multiple port forwards
tg add -n "dev-services" -h "dev-server.company.com" -u "developer" \
    --local-forward "8080:localhost:80,3306:db-internal:3306,5432:pg-db:5432"

# Remote port forwarding (expose local service to remote)
tg add -n "demo-server" -h "demo.company.com" -u "demo" \
    --remote-forward "8080:localhost:3000" \
    --notes "Expose local dev server on remote port 8080"
```

### Complex Real-World Examples

```bash
# Production database with full security
tg add -n "prod-db" \
    --host "prod-db-01.internal" \
    --hostname "prod-db-01.company.internal" \
    --user "produser" \
    --key "~/.ssh/production_key" \
    --proxy-jump "prod-bastion.company.com" \
    --local-forward "5432:prod-db-01.internal:5432" \
    --notes "Production PostgreSQL access via bastion with tunnel"

# Development full-stack environment
tg add -n "dev-full-stack" \
    --host "dev.company.com" \
    --user "developer" \
    --proxy-jump "dev-bastion.company.com" \
    --local-forward "3000:localhost:3000,8080:localhost:8080,5432:localhost:5432" \
    --notes "Full development stack: React (3000), API (8080), PostgreSQL (5432)"
```

### Connection Management

```bash
# Show detailed connection information
tg show prod-db
tg show 1  # By number from list

# Remove connections
tg remove prod-db
tg remove 1  # By number

# Configure default settings
tg config

# View generated SSH configuration
cat ~/.ssh/config.tengingarstjori
```

## CLI Commands

### Core Commands
- `tg add` - Add new SSH connection (supports ProxyJump, port forwarding, notes)
- `tg list` - List all connections with optional detailed view (`--detailed`, `--format`)
- `tg show <connection>` - Show detailed connection information
- `tg remove <connection>` - Remove connection by name or number
- `tg config` - Manage default settings (SSH keys, etc.)

### Management Commands
- `tg init` - Initialize Tengingarstjóri and SSH config integration
- `tg refresh` - Update SSH config file with current connections
- `tg fix-config` - Fix corrupted SSH configuration
- `tg reset` - Restore original SSH config (before Tengingarstjóri)

### Enhanced Options
```bash
# List command options
tg list --detailed          # Show notes, proxy, port forwarding
tg list --format compact    # Space-efficient output
tg list --format json       # JSON output for scripting
tg list -d -f compact       # Both options combined

# Add command supports advanced SSH features
tg add --proxy-jump "bastion.company.com"           # Jump server
tg add --local-forward "3306:localhost:3306"        # Port tunnel
tg add --remote-forward "8080:localhost:3000"       # Reverse tunnel
tg add --notes "Production database server"         # Connection notes
```

## Python API

Tengingarstjóri can also be used as a Python library:

```python
from tengingarstjori import SSHConfigManager, SSHConnection

# Create a config manager
config_manager = SSHConfigManager()

# Create a new connection
connection = SSHConnection(
    name="api-server",
    host="api.company.com",
    user="apiuser",
    port=2222,
    proxy_jump="bastion.company.com",
    local_forward="8080:localhost:8080",
    notes="API server with tunnel"
)

# Add the connection
config_manager.add_connection(connection)

# List all connections
connections = config_manager.list_connections()

# Get a specific connection
conn = config_manager.get_connection_by_name("api-server")
```

## Testing Your Setup

### Quick Feature Test
```bash
# Run the automated feature demonstration
chmod +x test_features.sh
./test_features.sh

# Reset for clean testing
./reset_tg.sh
```

### Manual Testing
```bash
# Test basic functionality
tg init
tg add -n "test-server" -h "example.com" -u "user"
tg list
tg show test-server

# Test advanced features
tg add -n "test-proxy" -h "internal.example.com" -u "admin" \
    --proxy-jump "bastion.example.com" \
    --local-forward "3306:localhost:3306" \
    --notes "Test database access via bastion"

tg list --detailed
```

### Verify SSH Configuration
```bash
# Check generated SSH config
cat ~/.ssh/config.tengingarstjori

# Test actual SSH connection
ssh test-server

# Test with debug output
ssh -vvv test-server
```

## Development

### Installing for Development

```bash
# Clone the repository
git clone https://github.com/yourusername/tengingarstjori.git
cd tengingarstjori

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run code quality checks
black src tests
flake8 src tests
mypy src
```

### Build and Test Package

```bash
# Build package
python -m build

# Test package
python -m twine check dist/*

# Install and test
pip install dist/*.whl
tg --help
```

## Troubleshooting

### Common Issues

**Connection fails through bastion:**
```bash
# Test bastion connectivity first
ssh bastion.company.com

# Test ProxyJump manually
ssh -J bastion.company.com user@target-host
```

**Port forwarding not working:**
```bash
# Check if ports are listening
netstat -an | grep LISTEN
lsof -i :3306  # Check specific port

# Test database connection through tunnel
mysql -h localhost -P 3306 -u username -p
```

**SSH config issues:**
```bash
# Fix corrupted configuration
tg fix-config

# Reset to original state
tg reset

# Regenerate managed config
tg refresh
```

### File Locations
- **Main SSH config**: `~/.ssh/config`
- **Managed config**: `~/.ssh/config.tengingarstjori`
- **Backup**: `~/.ssh/config.backup`
- **Tengingarstjóri data**: `~/.tengingarstjori/`
- **Connection database**: `~/.tengingarstjori/connections.json`

## Additional Resources

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Comprehensive usage guide
- **[PYPI_PUBLISHING_GUIDE.md](PYPI_PUBLISHING_GUIDE.md)** - Guide for maintainers
- **[CHANGELOG.md](CHANGELOG.md)** - Detailed change history

## Development Commands

- `mise run test` - Run tests with coverage
- `mise run lint` - Check code quality
- `mise run format` - Format code
- `mise run validate` - Full validation suite
- `mise run validate:quick` - Quick validation

## Development Workflow

```bash
# Daily development workflow
mise run validate:quick    # Quick checks before starting
# ... make changes ...
mise run test             # Run tests with coverage
mise run lint             # Check code quality
mise run validate         # Full validation before commit
```

## Contributing

1. See the implementation phases in [PHASES.md](PHASES.md)
2. Ensure all tests pass: `mise run test`
3. Check code quality: `mise run lint`
4. Run full validation: `mise run validate`
5. Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Development Environment

Created with Claude Project CLI and designed for seamless SSH workflow integration. Enhanced with comprehensive testing, code quality checks, and automated validation.

For detailed development setup, see [DEVELOPMENT.md](DEVELOPMENT.md).
