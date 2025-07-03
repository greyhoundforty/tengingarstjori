# Implementation Guide: Adding --no-color Flag

## Version Planning
- **Current**: 0.1.0
- **Next release**: 0.2.0 (MINOR - new feature)
- **Reason**: Adding backward-compatible functionality

## Implementation Steps

### 1. Update CLI with Global Option
```python
# In cli.py
@click.group()
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.version_option(version="0.2.0")
@click.pass_context
def cli(ctx, no_color):
    """Tengingarstjóri - SSH Connection Manager."""
    # Ensure context object exists
    ctx.ensure_object(dict)
    ctx.obj['no_color'] = no_color

    # Configure console based on flag
    if no_color:
        global console
        console = Console(color_system=None)
```

### 2. Add Configuration Setting
```python
# In config_manager.py - add to settings management
def get_color_setting(self) -> bool:
    """Get color preference from settings."""
    return self.get_setting("use_color", True)

def set_color_setting(self, use_color: bool):
    """Set color preference in settings."""
    self.update_setting("use_color", use_color)
```

### 3. Update Commands to Use Context
```python
# In each command function
@cli.command()
@click.pass_context
def list(ctx, detailed, format):
    """List all SSH connections."""
    no_color = ctx.obj.get('no_color', False)

    # Use configuration if flag not provided
    if not no_color:
        config_manager = SSHConfigManager()
        no_color = not config_manager.get_color_setting()

    # Configure console for this command
    if no_color:
        local_console = Console(color_system=None)
    else:
        local_console = console

    # Use local_console for output
    local_console.print("SSH Connections:")
```

### 4. Add to Config Command
```python
# Add color configuration to the config command
@cli.command()
def config():
    """Configure Tengingarstjóri settings."""
    config_manager = SSHConfigManager()

    # ... existing code ...

    # Add color preference option
    if Confirm.ask("\n[cyan]Configure color output?[/cyan]"):
        current_color = config_manager.get_color_setting()
        new_color = Confirm.ask(
            f"[cyan]Use colored output?[/cyan]",
            default=current_color
        )
        config_manager.set_color_setting(new_color)
        console.print(f"[green]✓[/green] Color output: {'enabled' if new_color else 'disabled'}")
```

### 5. Environment Variable Support
```python
# Add environment variable support
import os

def should_use_color(ctx_no_color=False, config_manager=None):
    """Determine if color should be used based on multiple factors."""
    # Priority order:
    # 1. Command line flag --no-color
    # 2. Environment variable NO_COLOR
    # 3. Environment variable FORCE_COLOR
    # 4. Configuration setting
    # 5. TTY detection

    if ctx_no_color:
        return False

    if os.environ.get('NO_COLOR'):
        return False

    if os.environ.get('FORCE_COLOR'):
        return True

    if config_manager:
        return config_manager.get_color_setting()

    return sys.stdout.isatty()
```

### 6. Update Tests
```python
# Add tests for color functionality
def test_no_color_flag(isolated_cli_runner):
    """Test --no-color flag works."""
    result = isolated_cli_runner.invoke(cli, ["--no-color", "list"])
    # Verify no ANSI color codes in output
    assert '\x1b[' not in result.output

def test_color_configuration(config_manager):
    """Test color configuration persistence."""
    config_manager.set_color_setting(False)
    assert config_manager.get_color_setting() is False
```

## Release Checklist for 0.2.0

### Pre-Release
- [ ] Update version in `src/tengingarstjori/__init__.py` to "0.2.0"
- [ ] Update version in `pyproject.toml` to "0.2.0"
- [ ] Add feature to CHANGELOG.md
- [ ] Run full test suite: `mise run validate`
- [ ] Test color functionality manually
- [ ] Build package: `mise run build`
- [ ] Test installation: `mise run build:test-install`

### Release Process
- [ ] Commit changes: `git commit -m "Add --no-color flag and color configuration"`
- [ ] Tag release: `git tag v0.2.0`
- [ ] Test publish: `mise run publish:test`
- [ ] Verify test installation works
- [ ] Production publish: `mise run publish:prod`
- [ ] Push tags: `git push origin main --tags`
- [ ] Create GitHub release with changelog

### Post-Release
- [ ] Update documentation with new feature
- [ ] Announce on relevant channels
- [ ] Monitor for issues
- [ ] Plan next release (0.2.1 for bugs, 0.3.0 for next feature)

## Breaking Change Example (for 1.0.0+)

**What would require MAJOR version bump:**
```bash
# OLD (0.x.x): Default behavior
tg list  # Shows colored output by default

# NEW (hypothetical breaking change):
# If you changed default to no color
tg list  # Shows no color by default (BREAKING!)

# This would require 1.0.0 → 2.0.0
```

## Documentation Updates

Update README.md to document the new feature:

```markdown
### Color Output Control

Control colored terminal output:

```bash
# Disable colors for current command
tg --no-color list

# Configure color preference permanently
tg config  # Then choose color options

# Environment variables
NO_COLOR=1 tg list      # Disable colors
FORCE_COLOR=1 tg list   # Force colors
```
```

This approach gives users maximum flexibility while maintaining backward compatibility.
