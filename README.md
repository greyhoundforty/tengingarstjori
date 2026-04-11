# Tengingarstjóri - SSH Connection Manager

`Tengingarstjóri`, Icelandic for "Connection Manager", is a Python TUI based SSH connection manager that integrates seamlessly with your existing SSH configuration.

## Installation

### From PyPI (Recommended)

```bash
pip install tengingarstjori
```

### From Source

```bash
git clone https://github.com/greyhoundforty/tengingarstjori.git
cd tengingarstjori
pip install -e .
```

## Features

- 🔧 **Full SSH Connection Management**: Add, update, clone, and remove connections
- 📋 **Flexible List Views**: Table, compact, and JSON formats with tag/search/sort filtering
- ⚡ **Quick Connect**: `tg connect <name>` launches SSH and tracks usage stats
- 🚀 **ProxyJump Support**: Seamless bastion host and jump server configuration
- 🔀 **Port Forwarding**: Local and remote port forwarding with auto-corrected syntax
- 🔑 **Smart SSH Key Management**: Automatic key discovery and defaults
- 🔗 **Non-invasive SSH Config Integration**: Preserves your existing setup
- 📤 **Export / Import**: Backup and restore connections as JSON or SSH config format
- 🕓 **History & Health Checks**: `tg history` and `tg test` for usage tracking and connectivity
- 🎯 **Fast CLI Commands**: Intuitive `tg` prefix with rich output formatting

## Demo

<a href="https://asciinema.org/a/725744" target="_blank"><img src="https://asciinema.org/a/725744.svg" /></a>

## Quick Start

```bash
# Initialize Tengingarstjóri
tg init

# Add your first connection
tg add -n web-server -h 192.168.1.100 -u admin

# List connections
tg list

# Connect
tg connect web-server

# Or use SSH directly (tg manages the config)
ssh web-server
```

## Architecture

Rather than modifying your main SSH config directly, Tengingarstjóri will:

1. **Create a managed config file**: `~/.ssh/config.tengingarstjori`
2. **Add a single line to main config to include our new file**: `Include ~/.ssh/config.tengingarstjori`
3. **Manage connections separately**: All additions/changes go to the managed file
4. **Preserve your existing SSH setup**: Your existing SSH config remains untouched

## Security

Tengingarstjóri is designed to handle sensitive SSH configuration safely:

- **Restricted file permissions**: `connections.json`, `~/.ssh/config.tengingarstjori`, and the `~/.tengingarstjori/` config directory are created with `0600`/`0700` permissions atomically — there is no window where files are world-readable.
- **SSH config injection prevention**: All user-supplied fields (`name`, `host`, `user`, `identity_file`, `proxy_jump`, `extra_options`) are validated to reject newline characters before being written into the SSH config. Notes have newlines stripped. This prevents crafted values from injecting arbitrary SSH config directives.
- **Non-destructive config management**: Only a single `Include` line is added to your main `~/.ssh/config`. All managed connections live in a separate file that can be inspected, backed up, or removed independently.
- **Backup before changes**: A backup of your main SSH config is created at `~/.ssh/config.backup` before any modification.

## Usage Examples

### Basic Connection Management

```bash
# Add a simple connection
tg add -n web-server -h 192.168.1.100 -u admin

# Add with custom port and SSH key
tg add -n database -h db.company.com -u dbuser -p 2222 -k ~/.ssh/db_key

# Interactive mode (prompts for all options)
tg add

# Clone an existing connection with a new name
tg clone prod-web staging-web

# Connect (updates last_used / use_count, then execs ssh)
tg connect prod-web

# Preview the SSH command without connecting
tg connect prod-web --dry-run
```

### Listing and Filtering

```bash
# Standard table view
tg list

# Detailed view showing notes, proxy, and port forwarding
tg list --detailed

# Compact and JSON formats
tg list --format compact
tg list --format json

# Filter by tag
tg list --tag production

# Full-text search across name, host, user, and notes
tg list --search bastion

# Only connections never used
tg list --unused

# Sort by last used (most recent first)
tg list --sort last-used

# Combine filters
tg list --tag production --search web --sort use-count
```

### ProxyJump (Bastion/Jump Servers)

```bash
# Simple bastion host access
tg add -n internal-server -h 10.0.1.100 -u admin \
    --proxy-jump bastion.company.com

# Bastion with specific user and port
tg add -n secure-db -h 192.168.10.50 -u dbadmin \
    --proxy-jump "jumpuser@bastion.company.com:2222"

# Multi-hop through multiple servers
tg add -n deep-internal -h 172.16.5.10 -u root \
    --proxy-jump "jump1.company.com,user@jump2.internal.com"
```

### Port Forwarding

```bash
# Local port forwarding (tunnel remote service to local port)
tg add -n mysql-tunnel -h db-server.company.com -u dbuser \
    --local-forward "3306:localhost:3306"

# Multiple port forwards
tg add -n dev-services -h dev-server.company.com -u developer \
    --local-forward "8080:localhost:80,3306:db-internal:3306,5432:pg-db:5432"

# Remote port forwarding (expose local service to remote)
tg add -n demo-server -h demo.company.com -u demo \
    --remote-forward "8080:localhost:3000"
```

### Export, Import, and Backup

```bash
# Export all connections to JSON (stdout)
tg export

# Save to a file
tg export -o backup.json

# Export as raw SSH config blocks
tg export --format ssh-config

# Export without key paths (safe to share)
tg export --strip-keys -o safe-backup.json

# Import from a backup (skip existing by default)
tg import backup.json

# Import and overwrite conflicts
tg import backup.json --strategy overwrite

# Import and auto-rename conflicts (prod-web → prod-web-2)
tg import backup.json --strategy rename
```

### History, Health Checks, and Snippets

```bash
# Show recently used connections
tg history

# Show full history
tg history --all

# Test SSH connectivity for a single connection
tg test prod-web

# Test all connections
tg test --all

# Custom timeout
tg test prod-web --timeout 10

# Print the full SSH command for a connection
tg snippet staging-db

# Print the SSH config block
tg snippet staging-db --config

# Copy to clipboard (macOS)
tg snippet staging-db | pbcopy
```

### Complex Real-World Examples

```bash
# Production database with full security
tg add -n prod-db \
    --host prod-db-01.internal \
    --user produser \
    --key ~/.ssh/production_key \
    --proxy-jump prod-bastion.company.com \
    --local-forward "5432:prod-db-01.internal:5432" \
    --notes "Production PostgreSQL via bastion"

# Development full-stack environment
tg add -n dev-full-stack \
    --host dev.company.com \
    --user developer \
    --proxy-jump dev-bastion.company.com \
    --local-forward "3000:localhost:3000,8080:localhost:8080,5432:localhost:5432" \
    --notes "React (3000), API (8080), PostgreSQL (5432)"

# Clone prod config to staging and update the host
tg clone prod-db staging-db
tg update staging-db --host staging-db-01.internal --non-interactive
```

### Connection Management

```bash
# Show detailed connection information
tg show prod-db
tg show 1  # By number from list

# Update a connection (non-interactive)
tg update prod-db --host 10.0.1.20 --non-interactive

# Add or replace tags
tg update prod-db --tags "production,database" --non-interactive

# Remove a connection
tg remove prod-db
tg remove prod-db --force  # Skip confirmation

# View generated SSH configuration
cat ~/.ssh/config.tengingarstjori
```

## CLI Commands

### Connection Commands
| Command | Description |
|---------|-------------|
| `tg add` | Add a new SSH connection (interactive or via flags) |
| `tg update <name>` | Update fields on an existing connection |
| `tg clone <src> <name>` | Duplicate a connection with a new name |
| `tg remove <name>` | Remove a connection (`--force` skips confirmation) |
| `tg show <name>` | Show all fields and the generated SSH config block |
| `tg list` | List connections (`--tag`, `--search`, `--sort`, `--unused`, `--format`) |

### Workflow Commands
| Command | Description |
|---------|-------------|
| `tg connect <name>` | Connect via SSH; updates usage stats (`--dry-run` to preview) |
| `tg snippet <name>` | Print the SSH command or config block (`--config`) |
| `tg history` | Show recently used connections (`--all`, `-n <limit>`) |
| `tg test <name>` | Check SSH connectivity (`--all`, `--timeout`) |
| `tg export` | Export connections to JSON or SSH config (`-o`, `-f`, `--strip-keys`) |
| `tg import <file>` | Import connections from JSON (`--strategy skip\|overwrite\|rename`) |

### Setup & Maintenance Commands
| Command | Description |
|---------|-------------|
| `tg init` | Initialize and integrate with SSH config |
| `tg config` | Manage default settings (e.g. default SSH key) |
| `tg validate` | Check all connections for config issues |
| `tg refresh` | Regenerate `~/.ssh/config.tengingarstjori` |
| `tg fix-config` | Repair corrupted `Include` lines |
| `tg fix-forwards` | Auto-correct old-style port forwarding syntax |
| `tg reset` | Restore original SSH config from backup |

### File Locations
- **Main SSH config**: `~/.ssh/config`
- **Managed config**: `~/.ssh/config.tengingarstjori`
- **Backup**: `~/.ssh/config.backup`
- **Tengingarstjóri data**: `~/.tengingarstjori/`
- **Connection database**: `~/.tengingarstjori/connections.json`

## Additional Resources

- **[docs/demo.md](docs/demo.md)** - Live executable demo document (all commands with captured output)

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
