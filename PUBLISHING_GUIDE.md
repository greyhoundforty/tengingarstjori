# PyPI Publishing Guide for Tengingarstjóri

This guide covers everything you need to know about publishing `tengingarstjori` to PyPI and TestPyPI.

## Table of Contents

- [Understanding the Problem](#understanding-the-problem)
- [Quick Start: Publishing to PyPI](#quick-start-publishing-to-pypi)
- [Automated Publishing with GitHub Actions](#automated-publishing-with-github-actions)
- [Manual Publishing](#manual-publishing)
- [Testing with TestPyPI](#testing-with-testpypi)
- [Version Management](#version-management)
- [Troubleshooting](#troubleshooting)

---

## Understanding the Problem

### TestPyPI Installation Issue

When installing from TestPyPI, you may see dependency errors:

```bash
pip install -i https://test.pypi.org/simple/ tengingarstjori
# ERROR: Cannot install tengingarstjori because these package versions have conflicting dependencies
```

**Why this happens:**
- TestPyPI is a separate index from PyPI
- It doesn't contain your dependencies (textual, pydantic, rich, click)
- pip can't find the required packages on TestPyPI alone

**Solution:**
Use `--extra-index-url` to fall back to PyPI for dependencies:

```bash
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ tengingarstjori
```

This tells pip:
1. Try TestPyPI first for `tengingarstjori`
2. Fall back to PyPI for any missing packages (dependencies)

---

## Quick Start: Publishing to PyPI

### Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org/account/register/
2. **API Token**: Generate at https://pypi.org/manage/account/token/
3. **GitHub Secrets**: Add `PYPI_API_TOKEN` to your repository secrets

### First Time Setup

```bash
# 1. Update version in pyproject.toml
# Edit: version = "0.1.3"

# 2. Build the package
python3 -m build

# 3. Verify the build
python3 -m twine check dist/*

# 4. Upload to PyPI (manual method)
python3 -m twine upload dist/*
```

### Ongoing Releases (Automated)

Once GitHub Actions is configured:

```bash
# 1. Update version in pyproject.toml
# 2. Commit changes
git add pyproject.toml
git commit -m "Bump version to 0.1.3"
git push

# 3. Create a GitHub Release
# Go to: https://github.com/your-username/tengingarstjori/releases/new
# - Choose or create tag: v0.1.3
# - Release title: v0.1.3
# - Description: What's new in this release
# - Click "Publish release"

# GitHub Actions will automatically:
# - Run tests
# - Run code quality checks
# - Build the package
# - Publish to PyPI
```

---

## Automated Publishing with GitHub Actions

### Configuration

The workflow is defined in `.github/workflows/publish.yml` and has two jobs:

1. **`publish`** - Publishes to PyPI when a GitHub Release is created
2. **`test-pypi`** - Publishes to TestPyPI when a tag is pushed

### Setting Up GitHub Secrets

#### For PyPI (Production)

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Token name: `tengingarstjori-github-actions`
4. Scope: "Entire account" (or limit to this project after first upload)
5. Copy the token (starts with `pypi-`)

6. Add to GitHub:
   - Go to: `https://github.com/your-username/tengingarstjori/settings/secrets/actions`
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: Paste your token
   - Click "Add secret"

#### For TestPyPI (Optional)

1. Go to https://test.pypi.org/manage/account/token/
2. Follow the same steps as above
3. GitHub secret name: `TEST_PYPI_API_TOKEN`

### Publishing Workflow

#### To Production (PyPI)

```bash
# Method 1: Via GitHub Web Interface
1. Go to https://github.com/your-username/tengingarstjori/releases/new
2. Click "Choose a tag" → Type new tag (e.g., v0.1.3) → "Create new tag"
3. Release title: "v0.1.3" or "Release 0.1.3"
4. Add release notes describing changes
5. Click "Publish release"

# Method 2: Via GitHub CLI (if installed)
gh release create v0.1.3 --title "v0.1.3" --notes "Release notes here"
```

#### To TestPyPI

```bash
# Just push a tag (no release needed)
git tag v0.1.3-test
git push origin v0.1.3-test

# This triggers the test-pypi job
```

### Workflow Features

The automated workflow:

✅ Runs full test suite with coverage
✅ Runs code quality checks (black, flake8, mypy)
✅ Builds both wheel and source distribution
✅ Validates package with twine
✅ Publishes to PyPI automatically
✅ Provides verbose output for debugging

---

## Manual Publishing

For full control or one-off releases:

### Step 1: Prepare the Package

```bash
# Clean previous builds
rm -rf dist/ build/ src/*.egg-info

# Update version in pyproject.toml
# Edit the version field: version = "0.1.3"

# Build fresh distributions
python3 -m build
```

### Step 2: Verify the Build

```bash
# Check package integrity
python3 -m twine check dist/*

# Should see:
# Checking dist/tengingarstjori-0.1.3-py3-none-any.whl: PASSED
# Checking dist/tengingarstjori-0.1.3.tar.gz: PASSED
```

### Step 3: Test Installation Locally

```bash
# Create a fresh virtual environment
python3 -m venv test-install
source test-install/bin/activate

# Install from the wheel
pip install dist/tengingarstjori-0.1.3-py3-none-any.whl

# Test the CLI
tg --version
tg --help

# Cleanup
deactivate
rm -rf test-install
```

### Step 4: Upload to PyPI

```bash
# Set environment variables (one-time setup)
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-pypi-token-here

# Upload to PyPI
python3 -m twine upload dist/*

# Or upload interactively
python3 -m twine upload dist/*
# Username: __token__
# Password: your-token-here
```

### Step 5: Verify on PyPI

```bash
# Wait a minute for PyPI to process, then:
pip install --upgrade tengingarstjori

# Or install in a fresh environment
python3 -m venv verify-pypi
source verify-pypi/bin/activate
pip install tengingarstjori
tg --version
deactivate
rm -rf verify-pypi
```

---

## Testing with TestPyPI

TestPyPI is a separate instance of PyPI for testing. It's perfect for:
- Testing the release process
- Verifying package metadata
- Checking installation before production

### Upload to TestPyPI

```bash
# Build the package
python3 -m build

# Upload to TestPyPI
python3 -m twine upload --repository testpypi dist/*
```

### Install from TestPyPI

**IMPORTANT:** You must use `--extra-index-url` to get dependencies from PyPI:

```bash
pip install -i https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            tengingarstjori
```

**Why the extra flag?**
- TestPyPI doesn't have your dependencies (textual, pydantic, etc.)
- `--extra-index-url` tells pip to also check PyPI for missing packages
- Your package comes from TestPyPI, dependencies from PyPI

### Configure TestPyPI in ~/.pypirc

Create `~/.pypirc` for easier uploads:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = your-pypi-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your-testpypi-token
```

Then upload with:

```bash
python3 -m twine upload --repository testpypi dist/*
```

---

## Version Management

### Semantic Versioning

This project follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 0.1.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Updating the Version

Version is stored in `pyproject.toml`:

```toml
[project]
name = "tengingarstjori"
version = "0.1.3"  # ← Update this
```

### Pre-release Versions

For testing:

```toml
version = "0.1.3a1"  # Alpha
version = "0.1.3b1"  # Beta
version = "0.1.3rc1" # Release Candidate
```

### Version Checklist

Before releasing:

- [ ] Update version in `pyproject.toml`
- [ ] Update `CHANGELOG.md` with changes
- [ ] Commit version bump: `git commit -m "Bump version to 0.1.3"`
- [ ] Create git tag: `git tag v0.1.3`
- [ ] Push: `git push && git push --tags`
- [ ] Create GitHub Release

---

## Troubleshooting

### Issue: "File already exists on PyPI"

**Problem:** You can't re-upload the same version to PyPI.

**Solution:**
```bash
# Bump the version in pyproject.toml
version = "0.1.4"

# Rebuild
rm -rf dist/
python3 -m build

# Upload new version
python3 -m twine upload dist/*
```

### Issue: "Invalid or non-existent authentication"

**Problem:** PyPI token is incorrect or expired.

**Solution:**
1. Generate a new token at https://pypi.org/manage/account/token/
2. Update GitHub secret or local environment variable
3. Try upload again

### Issue: Dependencies not found when installing from TestPyPI

**Problem:** Using TestPyPI without fallback to PyPI.

**Solution:**
```bash
# Wrong:
pip install -i https://test.pypi.org/simple/ tengingarstjori

# Correct:
pip install -i https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            tengingarstjori
```

### Issue: Build fails with "No module named build"

**Problem:** `build` package not installed.

**Solution:**
```bash
# Install build tools
pip install --upgrade build twine

# Or use system python
python3 -m pip install --upgrade build twine
```

### Issue: Package includes unwanted files

**Problem:** Test files, docs, or other unwanted files in distribution.

**Solution:**
Check `MANIFEST.in` and rebuild:

```bash
# Clean everything
rm -rf dist/ build/ src/*.egg-info

# Rebuild
python3 -m build

# Inspect contents
tar -tzf dist/tengingarstjori-*.tar.gz | less
unzip -l dist/tengingarstjori-*.whl | less
```

### Issue: GitHub Actions workflow not running

**Problem:** Workflow enabled but doesn't trigger.

**Solutions:**
1. Verify the workflow file is in `.github/workflows/`
2. Check the trigger conditions match your action:
   - `publish` job: Requires a GitHub **Release** (not just a tag)
   - `test-pypi` job: Requires pushing a **tag**
3. Check GitHub Actions tab for errors
4. Verify repository permissions allow Actions

### Issue: Tests pass locally but fail in GitHub Actions

**Problem:** Environment differences.

**Solutions:**
```bash
# Run tests exactly as CI does
python -m pytest --cov=src/tengingarstjori -v

# Check Python version matches CI
python --version  # Should match workflow (3.11)

# Install exact dependencies as CI
pip install -e .[dev,test]
```

---

## Best Practices

### Pre-release Checklist

- [ ] All tests pass: `mise run test`
- [ ] Code quality checks pass: `mise run lint`
- [ ] Version updated in `pyproject.toml`
- [ ] `CHANGELOG.md` updated
- [ ] Changes committed and pushed
- [ ] Tag created (for automated workflow)

### Release Process

1. **Development**
   ```bash
   # Make changes
   mise run test
   mise run lint
   ```

2. **Version Bump**
   ```bash
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   git add pyproject.toml CHANGELOG.md
   git commit -m "Bump version to 0.1.3"
   git push
   ```

3. **Create Release**
   - GitHub UI: Create new release with tag v0.1.3
   - Or: `gh release create v0.1.3 --generate-notes`

4. **Verify**
   ```bash
   # Wait a few minutes, then:
   pip install --upgrade tengingarstjori
   tg --version
   ```

### Security

- ✅ Never commit API tokens to git
- ✅ Use GitHub Secrets for tokens in Actions
- ✅ Use environment variables or `~/.pypirc` for local publishing
- ✅ Limit token scope to single project when possible
- ✅ Rotate tokens periodically

---

## Quick Reference

### Build Commands

```bash
# Clean build
rm -rf dist/ build/ src/*.egg-info && python3 -m build

# Check build
python3 -m twine check dist/*
```

### Upload Commands

```bash
# PyPI
python3 -m twine upload dist/*

# TestPyPI
python3 -m twine upload --repository testpypi dist/*
```

### Install Commands

```bash
# From PyPI
pip install tengingarstjori

# From TestPyPI
pip install -i https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            tengingarstjori

# From local build
pip install dist/tengingarstjori-*.whl
```

### Git Commands

```bash
# Tag and release
git tag v0.1.3
git push origin v0.1.3

# Delete tag (if needed)
git tag -d v0.1.3
git push origin :refs/tags/v0.1.3
```

---

## Additional Resources

- [PyPI Help](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [GitHub Actions: PyPI Publish](https://github.com/marketplace/actions/pypi-publish)

---

## Support

If you encounter issues:

1. Check this guide's [Troubleshooting](#troubleshooting) section
2. Verify PyPI/TestPyPI status: https://status.python.org/
3. Review GitHub Actions logs in the Actions tab
4. Check package status on PyPI: https://pypi.org/project/tengingarstjori/

---

**Last Updated:** 2025-11-22
**Package Version:** 0.1.2
**Maintainer:** Ryan Tiffany
