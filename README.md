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

## Code Improvement Implementation Plan

### Phase 1: Critical Fixes ✅ COMPLETED
**Status**: FIXED
**Timeline**: Immediate (Done)

#### Issues Fixed:
- ✅ **String Escaping Bug**: Fixed literal `\\n` characters in `setup.py`
- ✅ **Exception Handling**: Added comprehensive exception hierarchy in `src/exceptions.py`
- ✅ **Development Workflow**: Enhanced `mise.toml` with better testing and validation commands

#### Changes Made:
1. **Fixed `src/setup.py`**:
   - Replaced escaped `\\n` with actual newlines
   - Added proper error handling with custom exceptions
   - Refactored into `SetupWizard` class for better organization
   - Added comprehensive logging and validation

2. **Created `src/exceptions.py`**:
   - Hierarchical exception system with `TengingarstjoriError` base class
   - Specific exceptions: `SSHConfigError`, `ConnectionError`, `ValidationError`, etc.
   - Better error messages with context and details

3. **Enhanced `.mise.toml`**:
   - Added comprehensive testing commands (`test:unit`, `test:integration`, `test:coverage`)
   - Enhanced code quality checks with `lint` and `validate` commands
   - Added smoke tests for quick validation
   - Better error reporting and progress indicators

### Phase 2: Enhanced Testing (NEXT PRIORITY)
**Status**: PLANNED
**Timeline**: 1-2 days
**Dependencies**: Phase 1 complete

#### Objectives:
- Achieve 90%+ test coverage
- Add integration tests for CLI workflows
- Implement property-based testing
- Add performance benchmarks

#### Implementation Tasks:
1. **Create comprehensive test suite**:
   ```bash
   mkdir -p tests/{unit,integration,fixtures}
   # Add integration tests for full CLI workflows
   # Add property-based tests with Hypothesis
   # Add performance benchmarks
   ```

2. **Test categories to implement**:
   - Unit tests for models and config manager
   - Integration tests for CLI commands
   - End-to-end workflow tests
   - Error condition and edge case tests
   - Performance and load tests

3. **Commands to add**:
   ```bash
   mise run test:integration  # Full CLI workflow tests
   mise run test:performance  # Performance benchmarks
   mise run test:edge-cases   # Edge case testing
   ```

### Phase 3: Code Organization Refactoring
**Status**: PLANNED
**Timeline**: 2-3 days
**Dependencies**: Phase 2 complete

#### Objectives:
- Split large CLI module into focused components
- Add structured logging throughout application
- Implement configuration validation
- Enhance error handling across all modules

#### Implementation Tasks:
1. **Modularize CLI structure**:
   ```
   src/cli/
   ├── __init__.py          # Main CLI entry point
   ├── commands/
   │   ├── connection.py    # add, list, show, remove
   │   ├── config.py        # config, init commands
   │   └── maintenance.py   # fix-config, refresh
   └── utils.py             # Shared utilities
   ```

2. **Add structured logging**:
   - Configure Rich-based logging
   - Add debug logging throughout
   - Implement log levels and file output

3. **Configuration management**:
   - Centralize constants in `src/config.py`
   - Add settings validation
   - Implement configuration migration

### Phase 4: Pre-commit Hooks and CI/CD
**Status**: PLANNED
**Timeline**: 1-2 days
**Dependencies**: Phase 3 complete

#### Objectives:
- Implement automated code quality enforcement
- Set up pre-commit hooks for all quality checks
- Add continuous integration pipeline
- Ensure consistent development workflow

#### Implementation Tasks:
1. **Pre-commit configuration**:
   ```bash
   # Create .pre-commit-config.yaml
   # Install hooks for: Black, Flake8, MyPy, Bandit
   # Add automated testing on commit
   ```

2. **Quality assurance**:
   - Code formatting (Black, isort)
   - Linting (Flake8 with plugins)
   - Type checking (MyPy)
   - Security scanning (Bandit)
   - Import sorting and organization

3. **CI/CD pipeline**:
   - GitHub Actions workflow
   - Automated testing on pull requests
   - Code coverage reporting
   - Security vulnerability scanning

### Phase 5: Advanced Features and Polish
**Status**: PLANNED
**Timeline**: 2-3 days
**Dependencies**: Phase 4 complete

#### Objectives:
- Add advanced SSH features support
- Implement connection import/export
- Add configuration backup and restore
- Enhance user experience

#### Implementation Tasks:
1. **Advanced SSH features**:
   - SSH agent integration
   - Jump host chaining
   - Connection multiplexing
   - Custom SSH options

2. **Data management**:
   - Import from existing SSH configs
   - Export connections to various formats
   - Backup and restore functionality
   - Connection synchronization

3. **User experience**:
   - Interactive TUI mode
   - Connection health checking
   - Usage analytics and insights
   - Shell completion scripts

## Exception Handling Implementation

### Current Exception Strategy
The application now uses a hierarchical exception system with these key benefits:

1. **Specific Error Types**: Each type of error has its own exception class
2. **Better Error Messages**: Exceptions include context and suggestions
3. **Graceful Degradation**: Proper error recovery and user feedback
4. **Debug Information**: Detailed logging for troubleshooting

### Exception Hierarchy
```python
TengingarstjoriError (base)
├── SSHConfigError          # SSH configuration issues
├── ConnectionError         # Connection management issues
│   ├── DuplicateConnectionError
│   └── ConnectionNotFoundError
├── ValidationError         # Data validation issues
│   └── InvalidSSHKeyError
├── SetupError             # Initial setup issues
├── FileOperationError     # File system issues
├── CLIError              # CLI command issues
├── ConfigurationError    # App configuration issues
├── PermissionError       # Permission issues
└── BackupError           # Backup operation issues
```

### Usage Examples
```python
# Instead of generic exceptions:
raise Exception("Connection already exists")

# Use specific exceptions:
raise DuplicateConnectionError("web-server")

# With detailed context:
raise ValidationError("port", "99999", "Port must be between 1-65535")

# With error recovery suggestions:
try:
    config_manager.update_ssh_config()
except SSHConfigError as e:
    console.print(f"[red]SSH config error: {e}[/red]")
    console.print("[yellow]Try: tg fix-config[/yellow]")
```

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

## Implementation Progress

- ✅ **Phase 1 Complete**: Critical bugs fixed, exceptions added, development workflow enhanced
- 🚧 **Phase 2 Next**: Comprehensive testing suite
- 📋 **Phase 3 Planned**: Code organization and refactoring
- 📋 **Phase 4 Planned**: Pre-commit hooks and CI/CD
- 📋 **Phase 5 Planned**: Advanced features and polish

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

1. Follow the implementation phases in order
2. Ensure all tests pass: `mise run test`
3. Check code quality: `mise run lint`
4. Run full validation: `mise run validate`
5. Update documentation as needed

## Development Environment

Created with Claude Project CLI and designed for seamless SSH workflow integration. Enhanced with comprehensive testing, code quality checks, and automated validation.

For detailed development setup, see [DEVELOPMENT.md](DEVELOPMENT.md).
