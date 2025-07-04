# Development Guide - Tengingarstjóri

## Quick Development Setup

### 1. Environment Setup
```bash
# Set up development environment
mise run setup

# Check project info
mise run info
```

### 2. Development Workflow
```bash
# Install in development mode (creates 'tg' command)
mise run dev

# Run tests
mise run test

# Run tests with coverage
mise run tc

# Format code
mise run format

# Check code quality
mise run lint
```

### 3. Testing the CLI

#### Basic Testing
```bash
# Demo the application
mise run demo

# Test individual commands
mise run tg:init     # Initialize SSH integration
mise run tg:add      # Add SSH connection (interactive)
mise run tg:list     # List connections
mise run tg:config   # Configure settings
```

#### Manual Testing
```bash
# After installing in dev mode, you can use directly:
tg init
tg add
tg list
tg show 1
tg config
```

### 4. Test SSH Integration

The app will:
1. **Discover SSH keys** in `~/.ssh/`
2. **Create managed config**: `~/.ssh/config.tengingarstjóri`
3. **Add include line** to `~/.ssh/config`
4. **Preserve existing setup**

Test files created:
- `~/.tengingarstjóri/connections.json` (connection data)
- `~/.tengingarstjóri/settings.json` (app settings)
- `~/.ssh/config.tengingarstjóri` (SSH config)

### 5. Development Tasks

#### Code Quality
```bash
mise run lint       # Check code style and types
mise run format     # Auto-format with black
mise run test       # Run all tests
mise run tw         # Watch mode testing
```

#### Package Management
```bash
mise run uvi <package>     # Install new package
mise run uvf               # Update requirements.txt
mise run clean             # Clean build artifacts
mise run clean:full        # Clean everything including .venv
```

#### Distribution
```bash
mise run build           # Build wheel package
mise run install:global  # Install globally from build
```

### 6. Testing Checklist

- [ ] **Initialize**: `tg init` discovers SSH keys and sets up config
- [ ] **Add connection**: `tg add` creates SSH connection interactively
- [ ] **List connections**: `tg list` shows table of connections
- [ ] **Show details**: `tg show <name>` displays connection info
- [ ] **SSH integration**: Generated config works with `ssh <name>`
- [ ] **Settings**: `tg config` manages default SSH key
- [ ] **Remove**: `tg remove <name>` deletes connection

### 7. Architecture Overview

```
src/
├── models.py          # SSHConnection data model
├── config_manager.py  # SSH config integration & persistence
├── cli.py            # Click-based CLI commands
└── setup.py          # Initial setup wizard

tests/
├── test_models.py         # Model unit tests
└── test_config_manager.py # Manager integration tests
```

### 8. SSH Config Integration Details

**Safe Integration Method:**
1. Backup original `~/.ssh/config`
2. Create `~/.ssh/config.tengingarstjóri` (managed)
3. Add `Include ~/.ssh/config.tengingarstjóri` to main config
4. All `tg` changes only affect the managed file

**Example Generated Config:**
```
# ~/.ssh/config.tengingarstjóri
Host webserver
    HostName 192.168.1.10
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519
```

### 9. Common Development Commands

```bash
# Quick dev cycle
mise run setup && mise run dev && mise run test

# Full quality check
mise run lint && mise run test && mise run tc

# Reset and test from scratch
mise run clean:full && mise run setup && mise run dev && tg init
```

This setup gives you a complete isolated development environment for testing Tengingarstjóri before global installation!
