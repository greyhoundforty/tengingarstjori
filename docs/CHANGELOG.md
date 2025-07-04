# CHANGELOG

All notable changes to the Tengingarstjóri project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Enhanced List Command**: Added detailed view option to `tg list` command
  - `--detailed` / `-d` flag shows notes, proxy settings, port forwarding, and SSH keys
  - `--format` / `-f` option supports `table` (default) and `compact` formats
  - Examples: `tg list -d`, `tg list -f compact`, `tg list -d -f compact`
  - Detailed table view shows advanced options with color coding
  - Compact format provides space-efficient listing with optional details

- **ProxyJump and Port Forwarding Examples**: Comprehensive examples for advanced SSH features
  - Basic and multi-hop ProxyJump configurations
  - Local and remote port forwarding examples
  - Real-world scenarios for enterprise, cloud, and development environments
  - SOCKS proxy and dynamic forwarding examples
  - Troubleshooting tips and syntax reference

### Fixed
- **Critical**: Added missing `datetime` import in `cli.py` that was causing initialization failures
  - Error: `NameError: name 'datetime' is not defined` when creating SSH config file
  - Location: Line 50 in `init()` function
  - Solution: Added `from datetime import datetime` to imports section

### Changed
- **Cross-platform compatibility**: Updated sed commands in cleanup scripts to support both macOS and Linux
  - macOS requires `sed -i ''` (empty string after -i flag)
  - Linux uses `sed -i` (no empty string required)
  - Updated both bash cleanup script and manual cleanup commands
  - Added OS detection using `$OSTYPE` variable

### Added
- **Development Tools**: Created comprehensive cleanup and testing utilities
  - `cleanup_and_test_script.sh`: Full-featured cleanup and testing script
  - `manual_cleanup_commands.sh`: Quick manual cleanup commands
  - `reset_tg.sh`: Simple one-command reset script for easy testing
  - `test_features.sh`: Demonstration script for new list and proxy features
  - Cross-platform compatibility for macOS and Linux
  - Backup functionality before cleanup operations
  - Test cycle automation

### Technical Details

#### Files Modified
1. **src/cli.py**
   - Backup created: `src/cli.py.backup2`
   - Enhanced `list()` command with `--detailed` and `--format` options
   - Added helper functions `_display_connections_table()` and `_display_connections_compact()`
   - Updated `add()` command documentation with ProxyJump and port forwarding examples
   - Lines changed: ~150 lines added for enhanced list functionality

2. **Documentation and Examples**
   - `README.md`: Completely updated with comprehensive usage examples and enhanced features
   - `QUICK_REFERENCE.md`: Comprehensive quick reference guide
   - `proxy_jump_examples.sh`: Detailed examples for all advanced SSH features
   - `test_features.sh`: Automated demonstration script
   - Updated `CHANGELOG.md` with detailed change documentation

#### Implementation Details
The enhanced list command supports two output formats:
- **Table format** (default): Rich table with optional detailed columns
- **Compact format**: Space-efficient text output

Detailed mode shows:
- Advanced SSH options (ProxyJump, port forwarding) with color coding
- Connection notes and SSH key information
- Multi-line display for complex configurations

#### Testing Examples
```bash
# Test the new features
chmod +x test_features.sh reset_tg.sh
./test_features.sh

# Manual testing
tg add -n "test-proxy" -h "internal.example.com" -u "admin" \
    --proxy-jump "bastion.example.com" \
    --local-forward "3306:localhost:3306" \
    --notes "Test database access via bastion"

tg list --detailed
tg list -f compact
```

#### Root Cause Analysis
The original fix attempt introduced a datetime usage without importing the module:
```python
# This line was causing the error:
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# But datetime was not imported
```

#### Platform Compatibility Issues
- **macOS sed behavior**: Requires empty string after `-i` flag
  - Working: `sed -i '' 'pattern' file`
  - Fails: `sed -i 'pattern' file`
- **Linux sed behavior**: Works with or without empty string
  - Working: `sed -i 'pattern' file`
  - Also works: `sed -i '' 'pattern' file`

#### Testing Notes
- Error manifested during SSH config file creation in `init()` command
- Issue only occurred when SSH config file didn't exist and needed to be created
- Cleanup scripts tested on both macOS and Ubuntu systems

#### Future Considerations
- Consider using Python's `platform` module for more robust OS detection
- Add automated tests to catch missing imports
- Consider cross-platform file operations using Python instead of shell commands

## Summary

This update fixes the critical datetime import issue and provides robust cross-platform testing tools. The main changes ensure:

1. **Immediate fix**: `tg init` now works without datetime errors
2. **Better testing**: Easy cleanup and reset for development testing
3. **Cross-platform**: Works on both macOS and Linux systems
4. **Documentation**: Clear changelog for tracking changes

### Quick Testing Commands

For macOS:
```bash
# Quick reset
rm -rf ~/.tengingarstjori && rm -f ~/.ssh/config.tengingarstjori && rm -f ~/.ssh/config.backup && sed -i '' '/Include.*config\.tengingarstjori/d' ~/.ssh/config && echo "Ready for testing!"

# Test
tg init
```

For Linux:
```bash
# Quick reset
rm -rf ~/.tengingarstjori && rm -f ~/.ssh/config.tengingarstjori && rm -f ~/.ssh/config.backup && sed -i '/Include.*config\.tengingarstjori/d' ~/.ssh/config && echo "Ready for testing!"

# Test
tg init
```
