# Tengingarstjóri - SSH Connection Manager

`Tengingarstjóri`, Icelandic for "Connection Manager", is a Python TUI based SSH connection manager that integrates seamlessly with your existing SSH configuration.

## Features

- 🔧 Add, remove, edit, and delete SSH connections
- 📋 Beautiful TUI interface using Rich library
- 🔑 Smart SSH key management and defaults
- 🔗 Non-invasive SSH config integration
- 🎯 Fast CLI commands with `tg` prefix

## Demo

<a href="https://asciinema.org/a/725744" target="_blank"><img src="https://asciinema.org/a/725744.svg" /></a>

## Architecture

Rather than modifying your main SSH config directly, Tengingarstjóri will:

1. **Create a managed config file**: `~/.ssh/config.tengingarstjori`
2. **Add a single line to main config to include our new file**: `Include ~/.ssh/config.tengingarstjori`
3. **Manage connections separately**: All additions/changes go to the managed file
4. **Preserve your existing SSH setup**: Your existing SSH config remains untouched

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
- `tg refresh` - Update SSH config file with current connections
- `tg fix-config` - Fix corrupted SSH config file
- `tg reset` - Restore original SSH config (before Tengingarstjóri)

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

## Development Environment

Created with Claude Project CLI and designed for seamless SSH workflow integration. Enhanced with comprehensive testing, code quality checks, and automated validation.

For detailed development setup, see [DEVELOPMENT.md](DEVELOPMENT.md).
