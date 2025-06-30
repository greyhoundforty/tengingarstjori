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

## Initial Setup

The first run will:
1. Prompt for default SSH key locations
2. Scan for existing keys (`~/.ssh/id_*`)
3. Add the include line to your SSH config (if not present)
4. Create the managed config file

## CLI Commands

- `tg add` - Add new SSH connection
- `tg list` - List all connections
- `tg edit <name>` - Edit existing connection
- `tg remove <name>` - Remove connection
- `tg show <name>` - Show connection details
- `tg config` - Manage default settings

## Directory Structure

- `src/` - Source code
- `docs/` - Documentation
- `scripts/` - Utility scripts
- `chat_history/` - Claude conversation history
- `tests/` - Test files

## Development

Created with Claude Project CLI and designed for seamless SSH workflow integration.
