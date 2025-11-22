# Project Development Log

This file tracks major code and function changes made to the project.

## 2025-11-22 - PyPI Publishing Setup and Configuration

### Changes Made

1. **Enabled PyPI GitHub Actions Workflow** (`.github/workflows/publish.yml`)
   - Uncommented the `publish` job to enable automated PyPI publishing
   - Workflow now triggers on GitHub Releases
   - Includes full test suite, code quality checks, and automatic PyPI upload
   - Requires `PYPI_API_TOKEN` to be set in GitHub repository secrets

2. **Created Comprehensive Publishing Guide** (`PUBLISHING_GUIDE.md`)
   - Documented TestPyPI installation issue and solution
   - Provided complete manual publishing workflow
   - Explained automated GitHub Actions publishing process
   - Included version management best practices
   - Added troubleshooting section for common issues
   - Created quick reference for build, upload, and install commands

3. **Fixed Build Dependencies and mise Tasks** (`.mise.toml`)
   - Updated `setup` task to properly install dev dependencies with uv
   - Fixed all TestPyPI installation commands to include `--extra-index-url https://pypi.org/simple/`
   - Updated `build:deps` to use uv instead of pip
   - Added proper Ubuntu Docker testing task
   - Enhanced TestPyPI testing tasks with dependency fallback

4. **Created Ubuntu Installation Guide** (`UBUNTU_INSTALL.md`)
   - Comprehensive guide for Ubuntu "externally managed environment" issue
   - Documented three recommended installation methods (pipx, venv, user install)
   - Included TestPyPI installation with correct fallback syntax
   - Added building from source instructions
   - Extensive troubleshooting section
   - Docker testing examples

### Key Insights

**TestPyPI Dependency Issue:**
- TestPyPI doesn't contain project dependencies (textual, pydantic, rich, click)
- Solution: Use `--extra-index-url https://pypi.org/simple/` when installing from TestPyPI
- This allows pip to fall back to PyPI for missing dependencies

**Publishing Workflow:**
- **For Production (PyPI):** Create a GitHub Release → Automatically publishes via Actions
- **For Testing (TestPyPI):** Push a git tag → Automatically publishes via Actions
- Manual publishing supported via `python3 -m twine upload dist/*`

### Files Modified

- `.github/workflows/publish.yml` - Enabled automated PyPI publishing
- `PUBLISHING_GUIDE.md` - Created comprehensive publishing documentation
- `UBUNTU_INSTALL.md` - Created Ubuntu installation guide with externally-managed workarounds
- `.mise.toml` - Fixed build dependencies and TestPyPI installation commands
- Installed dev dependencies in venv: `uv pip install -e ".[dev,test]"`

### Next Steps

To complete PyPI setup:
1. Add `PYPI_API_TOKEN` to GitHub repository secrets
2. Update version in `pyproject.toml` when ready for next release
3. Create GitHub Release to trigger automated publishing
4. Update README.md to reference the new publishing guide

### Package Status

- Current version: 0.1.2
- Package successfully builds: ✅
- Twine validation passes: ✅
- Ready for PyPI publishing: ✅

---

## 2025-11-22 - GitHub Actions Integration and Debugging

### Changes Made

1. **Fixed GitHub Actions Workflow Triggers** (`.github/workflows/publish.yml`)
   - Added `push: tags:` trigger to enable TestPyPI publishing on tag push
   - Added condition `if: github.event_name == 'release'` to `publish` job
   - Now properly separates:
     - Tag push → TestPyPI (for testing)
     - Release → PyPI (for production)

2. **Added GitHub Actions mise Tasks** (`.mise.toml`)
   - `gh:status` - Check workflow status and recent runs
   - `gh:logs` - View logs from latest workflow run
   - `gh:watch` - Watch latest workflow run in real-time
   - `gh:releases` - List GitHub releases
   - `gh:tags` - List git tags and show creation commands
   - `gh:create-release` - Interactive release creation
   - Updated help task to include new GitHub Actions section

### Issue Diagnosed

**Problem:** Workflow wasn't triggering when pushing tags

**Root Cause:** The workflow only had `release:` as a trigger event, but didn't listen for tag pushes. The `test-pypi` job had the right condition but the workflow never started.

**Solution:** Added `push: tags: ['v*']` trigger to the workflow

### Workflow Behavior (After Fix)

**For TestPyPI:**
```bash
git tag v0.1.3-test
git push origin v0.1.3-test
# → Triggers test-pypi job → Publishes to TestPyPI
```

**For Production PyPI:**
```bash
gh release create v0.1.3 --generate-notes
# or use: mise run gh:create-release
# → Triggers publish job → Publishes to PyPI
```

### Files Modified

- `.github/workflows/publish.yml` - Fixed workflow triggers
- `.mise.toml` - Added 6 new GitHub Actions tasks
- Updated help output with GitHub Actions section
