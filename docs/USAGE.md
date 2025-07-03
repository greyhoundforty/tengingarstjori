# Tengingarstjóri Usage Guide

## Quick Start

1. **Install**: `./install.sh`
2. **Initialize**: `tg init`
3. **Add connection**: `tg add`
4. **Connect**: `ssh <connection-name>`

## Commands Reference

### Setup
```bash
tg init                    # Initial setup and SSH config integration
tg config                 # Manage settings (default SSH key, etc.)
```

### Connection Management
```bash
tg add                     # Add new SSH connection (interactive)
tg list                    # List all connections
tg show <name|number>      # Show detailed connection info
tg remove <name|number>    # Remove connection
```

### Examples

#### Adding a Simple Connection
```bash
tg add
# Prompts:
# Connection name: webserver
# Host/IP: 192.168.1.10
# Username: admin
# Port: 22
# ...
```

#### Adding an Advanced Connection
```bash
tg add
# Same prompts, plus:
# Add advanced options? y
# ProxyJump: bastion.example.com
# LocalForward: 8080:localhost:80
# Notes: Production web server
```

#### Using Connections
```bash
# After adding "webserver" connection:
ssh webserver              # Uses your SSH config automatically
```

## SSH Config Integration

Tengingarstjóri manages SSH connections by:

1. **Creating**: `~/.ssh/config.tengingarstjóri` (managed file)
2. **Adding one line** to `~/.ssh/config`: `Include ~/.ssh/config.tengingarstjóri`
3. **Preserving** your existing SSH configuration

### Example Generated Config
```
# ~/.ssh/config.tengingarstjóri
Host webserver
    HostName 192.168.1.10
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host database
    HostName db.internal.com
    User dbadmin
    Port 3306
    ProxyJump bastion.example.com
    IdentityFile ~/.ssh/db_key
```

## Configuration

### Default SSH Key
Set a default SSH key for new connections:
```bash
tg config
# Select from discovered keys or enter custom path
```

### Data Storage
- **Connections**: `~/.tengingarstjóri/connections.json`
- **Settings**: `~/.tengingarstjóri/settings.json`
- **SSH Config**: `~/.ssh/config.tengingarstjóri`

## Tips

1. **Backup**: Your original SSH config is backed up during setup
2. **Multiple Keys**: Each connection can use a different SSH key
3. **Organization**: Use descriptive names for easy identification
4. **Advanced Features**: Supports ProxyJump, port forwarding, and custom options
5. **Safety**: Original SSH config remains untouched

## Troubleshooting

### Command Not Found
```bash
# Check installation
pip list | grep tengingarstjori

# Reinstall if needed
pip install -e . --force-reinstall
```

### SSH Issues
```bash
# Test SSH connection directly
ssh -F ~/.ssh/config.tengingarstjóri <connection-name>

# Check generated config
cat ~/.ssh/config.tengingarstjóri
```

### Reset Setup
```bash
# Remove managed files (keeps connections data)
rm ~/.ssh/config.tengingarstjóri

# Run setup again
tg init
```
