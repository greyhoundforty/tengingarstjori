# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tengingarstjóri is an SSH Connection Manager written in Python that provides a CLI tool (`tg`) for managing SSH connections through a TUI interface. It integrates non-invasively with existing SSH configurations by creating a separate managed config file (`~/.ssh/config.tengingarstjori`) and including it in the main SSH config.

## Key Architecture

### Core Components
- **src/models.py**: Pydantic-based `SSHConnection` model with support for ProxyJump, port forwarding, and SSH options
- **src/config_manager.py**: `SSHConfigManager` handles SSH config file integration and JSON persistence
- **src/cli.py**: Click-based CLI with Rich formatting for the `tg` command
- **src/setup.py**: Initial setup wizard for SSH integration

### Configuration Management
- **Non-invasive SSH integration**: Creates `~/.ssh/config.tengingarstjori` and adds `Include` line to main config
- **Connection persistence**: Stores connections in `~/.tengingarstjori/connections.json`
- **Settings management**: App settings in `~/.tengingarstjori/settings.json`
- **SSH key discovery**: Automatically discovers SSH keys in `~/.ssh/`

## Development Commands

### Setup and Installation
```bash
mise run setup          # Install dependencies
mise run dev            # Install in development mode (creates 'tg' command)
```

### Testing
```bash
mise run test           # Run tests with coverage (main test command)
mise run test:unit      # Unit tests only
mise run test:cli       # CLI integration tests
mise run tc             # Comprehensive coverage analysis with HTML report
mise run test:smoke     # Quick smoke tests for basic functionality
mise run tw             # Watch mode testing
```

### Code Quality
```bash
mise run lint           # Comprehensive code quality checks (black, flake8, mypy, bandit)
mise run format         # Format code with black and isort
mise run lint:fix       # Auto-fix formatting issues
```

### Validation
```bash
mise run validate       # Complete validation suite (lint + smoke + unit + integration)
mise run validate:quick # Quick validation (format check + smoke test)
```

### CLI Testing
```bash
mise run tg:init        # Test initialization
mise run tg:add         # Test adding connections
mise run tg:list        # Test listing connections
mise run tg:config      # Test configuration
```

## SSH Integration Architecture

The application uses a safe, non-invasive approach to SSH config integration:

1. **Backup**: Creates `~/.ssh/config.backup` before any changes
2. **Managed Config**: All `tg` connections go to `~/.ssh/config.tengingarstjori`
3. **Include Integration**: Adds single `Include ~/.ssh/config.tengingarstjori` line to main config
4. **Preservation**: Existing SSH setup remains completely untouched

Generated SSH configs support:
- Basic connection parameters (host, user, port, key)
- ProxyJump for bastion/jump servers
- LocalForward and RemoteForward for port tunneling
- Custom SSH options via extra_options dict

## Testing Strategy

- **Unit tests**: Focus on models.py and config_manager.py core functionality
- **Integration tests**: Test CLI commands and SSH config generation
- **Smoke tests**: Quick validation of imports and basic functionality
- **Coverage target**: 80% for comprehensive coverage, 50% for basic testing

## Dependencies

- **Core**: textual, rich, pydantic, click
- **Dev**: pytest, black, flake8, mypy
- **Optional**: bandit (security), isort (import sorting)

## File Structure

```
src/
├── models.py          # SSHConnection Pydantic model
├── config_manager.py  # SSH config integration & JSON persistence  
├── cli.py            # Click CLI commands with Rich output
└── setup.py          # Initial setup wizard

tests/
├── test_models.py         # Model validation and serialization
├── test_config_manager.py # Config file operations and SSH integration
└── test_cli.py           # CLI command testing
```

## Common Patterns

- All CLI commands use Rich console for formatted output
- SSH connections are validated using Pydantic models
- Configuration changes are atomic (backup, modify, verify)
- JSON persistence with datetime serialization support
- Error handling with custom exceptions in src/exceptions.py