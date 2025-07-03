#!/usr/bin/env python3
"""
Build script for Tengingarstjóri package.

This script helps with building, testing, and publishing the package.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"{'=' * 50}")
    print(f"Running: {' '.join(cmd)}")
    if description:
        print(f"Description: {description}")
    print(f"{'=' * 50}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def clean_build():
    """Clean build artifacts."""
    print("🧹 Cleaning build artifacts...")

    # Remove build directories
    for pattern in ["build", "dist", "*.egg-info"]:
        cmd = ["rm", "-rf"] + list(Path(".").glob(pattern))
        if cmd[2:]:  # Only run if there are files to remove
            subprocess.run(cmd, check=False)

    # Remove Python cache
    cmd = [
        "find",
        ".",
        "-name",
        "__pycache__",
        "-type",
        "d",
        "-exec",
        "rm",
        "-rf",
        "{}",
        "+",
    ]
    subprocess.run(cmd, check=False)

    cmd = ["find", ".", "-name", "*.pyc", "-delete"]
    subprocess.run(cmd, check=False)

    print("✅ Build artifacts cleaned")


def run_tests():
    """Run the test suite."""
    print("🧪 Running tests...")

    # Run tests with coverage
    cmd = [
        "python",
        "-m",
        "pytest",
        "--cov=src/tengingarstjori",
        "--cov-report=html",
        "--cov-report=term",
        "-v",
    ]

    if not run_command(cmd, "Running test suite with coverage"):
        return False

    print("✅ Tests passed")
    return True


def run_linting():
    """Run code quality checks."""
    print("🔍 Running code quality checks...")

    # Run black
    if not run_command(
        ["python", "-m", "black", "--check", "src", "tests"], "Checking code formatting"
    ):
        print("❌ Code formatting issues found. Run 'black src tests' to fix.")
        return False

    # Run flake8
    if not run_command(
        ["python", "-m", "flake8", "src", "tests"], "Checking code style"
    ):
        return False

    # Run mypy
    if not run_command(["python", "-m", "mypy", "src"], "Checking type hints"):
        return False

    print("✅ Code quality checks passed")
    return True


def build_package():
    """Build the package."""
    print("📦 Building package...")

    # Clean first
    clean_build()

    # Build package
    if not run_command(
        ["python", "-m", "build"], "Building wheel and source distribution"
    ):
        return False

    print("✅ Package built successfully")
    return True


def check_package():
    """Check package integrity."""
    print("🔍 Checking package integrity...")

    # Check with twine
    if not run_command(
        ["python", "-m", "twine", "check", "dist/*"], "Checking package integrity"
    ):
        return False

    print("✅ Package integrity check passed")
    return True


def install_dev():
    """Install package in development mode."""
    print("🔧 Installing in development mode...")

    if not run_command(
        ["python", "-m", "pip", "install", "-e", ".[dev]"],
        "Installing in development mode",
    ):
        return False

    print("✅ Development installation complete")
    return True


def test_install():
    """Test the installed package."""
    print("🧪 Testing installed package...")

    # Test import
    if not run_command(
        ["python", "-c", "import tengingarstjori; print('Import successful')"],
        "Testing package import",
    ):
        return False

    # Test CLI
    if not run_command(["tg", "--help"], "Testing CLI command"):
        return False

    print("✅ Package installation test passed")
    return True


def publish_test():
    """Publish to Test PyPI."""
    print("🚀 Publishing to Test PyPI...")

    if not run_command(
        ["python", "-m", "twine", "upload", "--repository", "testpypi", "dist/*"],
        "Publishing to Test PyPI",
    ):
        return False

    print("✅ Published to Test PyPI")
    return True


def publish_prod():
    """Publish to production PyPI."""
    print("🚀 Publishing to production PyPI...")

    # Confirm with user
    response = input("Are you sure you want to publish to production PyPI? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Publication cancelled")
        return False

    if not run_command(
        ["python", "-m", "twine", "upload", "dist/*"], "Publishing to production PyPI"
    ):
        return False

    print("✅ Published to production PyPI")
    return True


def main():
    """Run the main script."""
    if len(sys.argv) < 2:
        print("Usage: python build.py <command>")
        print("Commands:")
        print("  clean     - Clean build artifacts")
        print("  test      - Run tests")
        print("  lint      - Run code quality checks")
        print("  build     - Build package")
        print("  check     - Check package integrity")
        print("  dev       - Install in development mode")
        print("  test-install - Test installed package")
        print("  publish-test - Publish to Test PyPI")
        print("  publish-prod - Publish to production PyPI")
        print("  all       - Run all checks and build")
        return

    command = sys.argv[1]

    if command == "clean":
        clean_build()
    elif command == "test":
        if not run_tests():
            sys.exit(1)
    elif command == "lint":
        if not run_linting():
            sys.exit(1)
    elif command == "build":
        if not build_package():
            sys.exit(1)
    elif command == "check":
        if not check_package():
            sys.exit(1)
    elif command == "dev":
        if not install_dev():
            sys.exit(1)
    elif command == "test-install":
        if not test_install():
            sys.exit(1)
    elif command == "publish-test":
        if not publish_test():
            sys.exit(1)
    elif command == "publish-prod":
        if not publish_prod():
            sys.exit(1)
    elif command == "all":
        steps = [
            ("Cleaning", clean_build),
            ("Testing", run_tests),
            ("Linting", run_linting),
            ("Building", build_package),
            ("Checking", check_package),
        ]

        for step_name, step_func in steps:
            print(f"\n{'=' * 20} {step_name} {'=' * 20}")
            if not step_func():
                print(f"❌ {step_name} failed")
                sys.exit(1)

        print("\n🎉 All checks passed! Package is ready for publishing.")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
