# Tengingarstjóri - SSH Connection Manager

A TUI-based SSH connection manager that integrates seamlessly with your existing SSH configuration.

## Features

- 🔧 Add, remove, edit, and delete SSH connections
- 📋 Beautiful TUI interface using Rich library
- 🔑 Smart SSH key management and defaults
- 🔗 Non-invasive SSH config integration
- 🎯 Fast CLI commands with `tg` prefix

## Project Overview

**Name**: Tengingarstjóri (Icelandic for "Connection Manager")
**CLI Command**: `tg`
**Purpose**: Python TUI application to manage SSH connections with smart SSH config integration

## Architecture

Rather than modifying your main SSH config directly, Tengingarstjóri:

1. **Creates a managed config file**: `~/.ssh/config.tengingarstjóri`
2. **Adds one line to main config**: `Include ~/.ssh/config.tengingarstjóri`
3. **Manages connections separately**: All additions/changes go to the managed file
4. **Preserves your setup**: Your existing SSH config remains untouched

## Quick Start

```bash
# Install dependencies
mise run setup

# Install in development mode
mise run dev

# Initialize SSH integration
tg init

# Add your first connection
tg add

# List connections
tg list
```

## CLI Commands

- `tg add` - Add new SSH connection
- `tg list` - List all connections
- `tg edit <n>` - Edit existing connection
- `tg remove <n>` - Remove connection
- `tg show <n>` - Show connection details
- `tg config` - Manage default settings

## Development Commands

- `mise run test` - Run tests with coverage
- `mise run lint` - Check code quality
- `mise run format` - Format code
- `mise run validate` - Full validation suite
- `mise run validate:quick` - Quick validation

## Directory Structure

```
tengingarstjóri/
├── src/                    # Source code
│   ├── cli.py             # CLI interface
│   ├── config_manager.py  # SSH config management
│   ├── models.py          # Data models
│   ├── setup.py           # Setup wizard (FIXED)
│   └── exceptions.py      # Exception hierarchy (NEW)
├── tests/                  # Test suite
│   ├── test_models.py     # Model tests
│   └── test_config_manager.py  # Manager tests
├── scripts/               # Development scripts
├── docs/                  # Documentation
├── .mise.toml            # Development tasks (ENHANCED)
└── README.md             # This file (UPDATED)
```

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

## Development Environment

Created with Claude Project CLI and designed for seamless SSH workflow integration. Enhanced with comprehensive testing, code quality checks, and automated validation.

For detailed development setup, see [DEVELOPMENT.md](DEVELOPMENT.md).
