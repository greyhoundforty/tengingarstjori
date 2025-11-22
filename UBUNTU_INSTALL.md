# Installing tengingarstjori on Ubuntu

This guide covers installing `tengingarstjori` on Ubuntu systems, including dealing with the "externally managed environment" restriction introduced in Ubuntu 23.04+.

## Table of Contents

- [Understanding the "Externally Managed" Error](#understanding-the-externally-managed-error)
- [Recommended Installation Methods](#recommended-installation-methods)
- [Quick Start (Ubuntu 22.04+)](#quick-start-ubuntu-2204)
- [Installation from PyPI](#installation-from-pypi)
- [Installation from TestPyPI](#installation-from-testpypi)
- [Building from Source](#building-from-source)
- [Troubleshooting](#troubleshooting)

---

## Understanding the "Externally Managed" Error

### What is this error?

Starting with Ubuntu 23.04 (and Debian 12+), you may see this error when trying to install packages with pip:

```bash
$ pip install tengingarstjori
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.
```

### Why does this happen?

Ubuntu now uses PEP 668 to prevent pip from installing packages globally, which can:
- Conflict with system package manager (apt)
- Break system tools that depend on specific Python packages
- Create dependency conflicts

### Solutions

There are **3 proper ways** to install Python packages on Ubuntu:

1. **Virtual Environment** (Recommended for development)
2. **pipx** (Recommended for CLI tools like tengingarstjori)
3. **User Installation** (Alternative)

❌ **NOT RECOMMENDED:** Using `--break-system-packages` flag

---

## Recommended Installation Methods

### Method 1: Using pipx (Best for CLI tools)

**pipx** installs CLI tools in isolated environments while making commands globally available.

```bash
# Install pipx
sudo apt update
sudo apt install pipx

# Ensure pipx is in PATH
pipx ensurepath

# Restart shell or reload profile
source ~/.bashrc  # or ~/.zshrc

# Install tengingarstjori
pipx install tengingarstjori

# Use the command globally
tg --version
```

**Advantages:**
- ✅ Globally available `tg` command
- ✅ Isolated environment (no conflicts)
- ✅ Easy to update: `pipx upgrade tengingarstjori`
- ✅ Easy to uninstall: `pipx uninstall tengingarstjori`

### Method 2: Virtual Environment (Best for development)

Use a virtual environment to isolate the package:

```bash
# Install python3-venv if needed
sudo apt update
sudo apt install python3-venv

# Create a virtual environment
python3 -m venv ~/venvs/tengingarstjori

# Activate the virtual environment
source ~/venvs/tengingarstjori/bin/activate

# Install the package
pip install tengingarstjori

# Use it (while venv is active)
tg --version

# Deactivate when done
deactivate
```

**To make it permanently available**, add an alias to your `~/.bashrc` or `~/.zshrc`:

```bash
# Add to ~/.bashrc
alias tg='~/venvs/tengingarstjori/bin/tg'

# Reload shell config
source ~/.bashrc

# Now 'tg' works anywhere
tg --version
```

### Method 3: User Installation (--user flag)

Install only for your user (not system-wide):

```bash
# Install to user directory
pip install --user tengingarstjori

# Add user bin to PATH if needed (add to ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"

# Reload shell
source ~/.bashrc

# Use it
tg --version
```

**Note:** This may still be restricted on some Ubuntu versions.

---

## Quick Start (Ubuntu 22.04+)

### For End Users (using pipx)

```bash
# One-time setup
sudo apt update && sudo apt install pipx
pipx ensurepath
source ~/.bashrc

# Install
pipx install tengingarstjori

# Verify
tg --version
tg --help
```

### For Developers (using venv)

```bash
# Clone the repository
git clone https://github.com/your-username/tengingarstjori.git
cd tengingarstjori

# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev,test]"

# Verify
tg --version
```

---

## Installation from PyPI

Once published to PyPI:

### Using pipx (Recommended)

```bash
pipx install tengingarstjori
```

### Using venv

```bash
python3 -m venv ~/tengingarstjori-env
source ~/tengingarstjori-env/bin/activate
pip install tengingarstjori
```

---

## Installation from TestPyPI

**IMPORTANT:** When installing from TestPyPI, you MUST use `--extra-index-url` to get dependencies from PyPI:

### Using pipx

```bash
pipx install \
  --index-url https://test.pypi.org/simple/ \
  --pip-args="--extra-index-url https://pypi.org/simple/" \
  tengingarstjori
```

### Using venv

```bash
# Create and activate virtual environment
python3 -m venv test-env
source test-env/bin/activate

# Install from TestPyPI with PyPI fallback for dependencies
pip install \
  -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  tengingarstjori

# Verify
tg --version
```

### Why --extra-index-url?

TestPyPI doesn't contain dependencies like `textual`, `pydantic`, `rich`, and `click`. The `--extra-index-url` flag tells pip:

1. Try TestPyPI first for `tengingarstjori`
2. Fall back to regular PyPI for dependencies

Without this, you'll get dependency errors.

---

## Building from Source

### Prerequisites

```bash
# Install required system packages
sudo apt update
sudo apt install -y \
  python3 \
  python3-pip \
  python3-venv \
  git
```

### Clone and Build

```bash
# Clone the repository
git clone https://github.com/your-username/tengingarstjori.git
cd tengingarstjori

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install build dependencies
pip install build twine wheel setuptools

# Build the package
python -m build

# Install locally
pip install dist/*.whl

# Verify
tg --version
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/your-username/tengingarstjori.git
cd tengingarstjori

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with all dev tools
pip install -e ".[dev,test]"

# Verify
tg --version

# Run tests
pytest

# Run linting
black --check src/ tests/
flake8 src/ tests/
mypy src/
```

---

## Troubleshooting

### Issue: "externally-managed-environment" error

**Problem:**
```
error: externally-managed-environment
× This environment is externally managed
```

**Solutions:**

1. **Use pipx (recommended):**
   ```bash
   sudo apt install pipx
   pipx install tengingarstjori
   ```

2. **Use virtual environment:**
   ```bash
   python3 -m venv ~/my-env
   source ~/my-env/bin/activate
   pip install tengingarstjori
   ```

3. **User install (may not work on all systems):**
   ```bash
   pip install --user tengingarstjori
   export PATH="$HOME/.local/bin:$PATH"
   ```

### Issue: Command 'tg' not found after installation

**Problem:**
Package installed but `tg` command not available.

**Solutions:**

1. **Check if PATH is set correctly:**
   ```bash
   # For pipx
   pipx ensurepath
   source ~/.bashrc

   # For user install
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc

   # For venv
   source path/to/venv/bin/activate
   ```

2. **Find where tg is installed:**
   ```bash
   find ~ -name tg -type f 2>/dev/null
   ```

3. **Create an alias (if using venv):**
   ```bash
   echo 'alias tg="~/venvs/tengingarstjori/bin/tg"' >> ~/.bashrc
   source ~/.bashrc
   ```

### Issue: Dependencies not found when installing from TestPyPI

**Problem:**
```
ERROR: Could not find a version that satisfies the requirement textual>=3.5.0
```

**Solution:**
Use `--extra-index-url` to fall back to PyPI for dependencies:

```bash
pip install \
  -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  tengingarstjori
```

### Issue: Python version too old

**Problem:**
```
ERROR: Package requires Python >=3.10
```

**Solution:**

Ubuntu 22.04+ has Python 3.10+. For older versions:

```bash
# Check your Python version
python3 --version

# If < 3.10, use deadsnakes PPA
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv

# Use the specific version
python3.12 -m venv .venv
source .venv/bin/activate
pip install tengingarstjori
```

### Issue: Permission denied errors

**Problem:**
```
ERROR: Could not install packages due to an PermissionError
```

**Solutions:**

1. **Use virtual environment (recommended):**
   ```bash
   python3 -m venv ~/my-env
   source ~/my-env/bin/activate
   pip install tengingarstjori
   ```

2. **Use --user flag:**
   ```bash
   pip install --user tengingarstjori
   ```

3. **Don't use sudo with pip** (creates permission issues)

---

## Docker Testing

To test installation on a fresh Ubuntu system:

```bash
# Test on Ubuntu 24.04
docker run -it --rm ubuntu:24.04 bash

# Inside container:
apt-get update
apt-get install -y python3 python3-pip python3-venv
python3 -m venv /tmp/venv
source /tmp/venv/bin/activate
pip install -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  tengingarstjori
tg --version
```

---

## Best Practices

### For End Users

1. **Use pipx** for installing CLI tools globally
2. Never use `sudo pip install`
3. Never use `--break-system-packages`

### For Developers

1. **Always use virtual environments** for development
2. Keep `.venv` in project directory
3. Add `.venv/` to `.gitignore`
4. Document activation steps in project README

### For CI/CD

1. Use virtual environments in containers
2. Pin dependency versions for reproducibility
3. Test on target Ubuntu versions

---

## Quick Reference

### Installation Commands

```bash
# Production (pipx)
pipx install tengingarstjori

# Development (venv)
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,test]"

# TestPyPI (with fallback)
pip install -i https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  tengingarstjori
```

### Activation

```bash
# Activate venv
source .venv/bin/activate

# Deactivate venv
deactivate

# Ensure pipx path
pipx ensurepath
```

### Verification

```bash
# Check installation
tg --version
tg --help

# Check Python version
python3 --version

# Check pip location
which pip
```

---

## Additional Resources

- [PEP 668 - Marking Python base environments as "externally managed"](https://peps.python.org/pep-0668/)
- [pipx documentation](https://pypa.github.io/pipx/)
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [Ubuntu Python Packaging Guide](https://packaging.python.org/en/latest/)

---

**Last Updated:** 2025-11-22
**Tested On:** Ubuntu 22.04, 24.04
**Python Version:** 3.10, 3.11, 3.12
