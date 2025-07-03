# PyPI Publishing Guide for Tengingarstjóri

This guide walks you through the complete process of publishing your Tengingarstjóri package to PyPI.

## Prerequisites

1. **Python 3.9+** installed
2. **Git** for version control
3. **PyPI account** at https://pypi.org/account/register/
4. **Test PyPI account** at https://test.pypi.org/account/register/

## Step 1: Set Up Your PyPI Accounts

### Create PyPI Accounts
```bash
# 1. Go to https://pypi.org/account/register/
# 2. Create your account
# 3. Enable 2FA (Two Factor Authentication)
# 4. Go to https://test.pypi.org/account/register/
# 5. Create your Test PyPI account
```

### Create API Tokens
```bash
# For PyPI:
# 1. Go to https://pypi.org/manage/account/token/
# 2. Create a new API token
# 3. Scope: "Entire account" (for first time)
# 4. Save the token securely

# For Test PyPI:
# 1. Go to https://test.pypi.org/manage/account/token/
# 2. Create a new API token
# 3. Scope: "Entire account"
# 4. Save the token securely
```

### Configure Authentication
Create `~/.pypirc` file:
```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-token-here
```

## Step 2: Prepare Your Package

### Update Version
Edit `src/tengingarstjori/__init__.py`:
```python
__version__ = "0.1.0"  # Update as needed
```

Edit `pyproject.toml`:
```toml
[project]
name = "tengingarstjori"
version = "0.1.0"  # Keep in sync with __init__.py
```

### Update Package Information
Edit `pyproject.toml` to customize:
- `authors` - Add your real name and email
- `homepage` - Update GitHub URL
- `description` - Refine if needed
- `keywords` - Add relevant keywords
- `classifiers` - Verify they're accurate

## Step 3: Local Testing

### Install Development Dependencies
```bash
pip install -e .[dev,test]
```

### Run Quality Checks
```bash
# Format code
black src tests

# Check linting
flake8 src tests

# Type checking
mypy src

# Run tests
pytest --cov=src/tengingarstjori --cov-report=html -v
```

### Build Package
```bash
python -m build
```

### Check Package
```bash
python -m twine check dist/*
```

### Test Local Installation
```bash
pip install dist/*.whl
python -c "import tengingarstjori; print('Success!')"
tg --help
```

## Step 4: Test on Test PyPI

### Upload to Test PyPI
```bash
python -m twine upload --repository testpypi dist/*
```

### Test Installation from Test PyPI
```bash
# Create a new virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ tengingarstjori

# Test functionality
python -c "import tengingarstjori; print('Test PyPI installation successful!')"
tg --help

# Deactivate and clean up
deactivate
rm -rf test-env
```

## Step 5: Publish to Production PyPI

### Final Checks
```bash
# Ensure all tests pass
python scripts/build.py all

# Verify package contents
tar -tzf dist/tengingarstjori-*.tar.gz | head -20
```

### Upload to Production PyPI
```bash
python -m twine upload dist/*
```

### Verify Publication
```bash
# Check on PyPI
open https://pypi.org/project/tengingarstjori/

# Test installation
pip install tengingarstjori
tg --help
```

## Step 6: Post-Publication

### Create GitHub Release
1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag: `v0.1.0` (matching your version)
4. Title: `Release v0.1.0`
5. Description: Summary of changes
6. Click "Publish release"

### Update Documentation
Update your README.md with installation instructions:
```markdown
## Installation

Install Tengingarstjóri from PyPI:

```bash
pip install tengingarstjori
```

## Usage

Initialize and start using:

```bash
tg init
tg add -n myserver -h example.com -u myuser
tg list
```

## Automation with GitHub Actions

The project includes GitHub Actions workflows for:
- **Testing**: Runs on every push/PR
- **Publishing**: Triggers on GitHub releases

### Set Up GitHub Actions

1. **Add PyPI tokens to GitHub secrets**:
   - Go to your repository settings
   - Navigate to "Secrets and variables" → "Actions"
   - Add these secrets:
     - `PYPI_API_TOKEN`: Your production PyPI token
     - `TEST_PYPI_API_TOKEN`: Your Test PyPI token

2. **Enable trusted publishing** (recommended):
   - Go to PyPI → "Your projects" → "tengingarstjori"
   - Navigate to "Publishing" → "Add a new publisher"
   - Set up GitHub Actions trusted publishing

## Package Maintenance

### Version Updates
Follow semantic versioning:
- `0.1.0` → `0.1.1` (patch: bug fixes)
- `0.1.1` → `0.2.0` (minor: new features)
- `0.2.0` → `1.0.0` (major: breaking changes)

### Update Process
1. Update version in `src/tengingarstjori/__init__.py`
2. Update version in `pyproject.toml`
3. Update `CHANGELOG.md`
4. Run tests: `python scripts/build.py all`
5. Commit changes: `git commit -m "Release v0.1.1"`
6. Tag release: `git tag v0.1.1`
7. Push: `git push origin main --tags`
8. Create GitHub release (triggers auto-publish)

## Troubleshooting

### Common Issues

**"Package already exists" error**:
- You can't replace an existing version
- Increment the version number and try again

**"Invalid authentication" error**:
- Check your API tokens in `~/.pypirc`
- Ensure tokens haven't expired
- Verify you're using the correct repository

**"Package name not available" error**:
- The package name is taken
- Choose a different name in `pyproject.toml`
- Check availability: `pip search tengingarstjori`

**Import errors after installation**:
- Check your package structure
- Verify `__init__.py` files exist
- Test locally first: `pip install -e .`

**Missing dependencies**:
- Check `pyproject.toml` dependencies
- Test in a clean environment
- Verify all required packages are listed

### Build Script Usage

The `scripts/build.py` script automates common tasks:

```bash
# Clean build artifacts
python scripts/build.py clean

# Run tests
python scripts/build.py test

# Run linting
python scripts/build.py lint

# Build package
python scripts/build.py build

# Check package integrity
python scripts/build.py check

# Install in development mode
python scripts/build.py dev

# Test installed package
python scripts/build.py test-install

# Publish to Test PyPI
python scripts/build.py publish-test

# Publish to production PyPI
python scripts/build.py publish-prod

# Run all checks and build
python scripts/build.py all
```

## Security Best Practices

1. **Use API tokens** instead of passwords
2. **Enable 2FA** on both PyPI accounts
3. **Use scoped tokens** when possible
4. **Store tokens securely** (not in code)
5. **Rotate tokens regularly**
6. **Use trusted publishing** with GitHub Actions

## Monitoring and Analytics

### PyPI Statistics
- View download stats at https://pypi.org/project/tengingarstjori/
- Use tools like `pypistats` for detailed analytics
- Monitor for security vulnerabilities

### GitHub Insights
- Monitor repository traffic and clones
- Track issues and pull requests
- Review GitHub Actions workflow runs

## Next Steps

1. **Set up continuous integration** with GitHub Actions
2. **Create comprehensive documentation** with MkDocs
3. **Add more tests** to increase coverage
4. **Consider semantic release** for automated versioning
5. **Set up dependabot** for dependency updates
6. **Monitor security** with tools like Snyk or GitHub Security

## Support and Community

- **Documentation**: Include link to full documentation
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Enable GitHub Discussions for questions
- **Contributing**: Create CONTRIBUTING.md with guidelines
- **Code of Conduct**: Add CODE_OF_CONDUCT.md

## Package Structure Summary

Your final package structure should look like:

```
tengingarstjóri/
├── src/
│   └── tengingarstjori/
│       ├── __init__.py
│       ├── cli.py
│       ├── config_manager.py
│       ├── models.py
│       ├── exceptions.py
│       └── setup.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_config_manager.py
│   ├── test_exceptions.py
│   └── test_package_integration.py
├── scripts/
│   └── build.py
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── publish.yml
├── pyproject.toml
├── MANIFEST.in
├── README.md
├── CHANGELOG.md
├── LICENSE
└── requirements.txt
```

This structure follows Python packaging best practices and ensures your package is professional, maintainable, and ready for PyPI distribution.
