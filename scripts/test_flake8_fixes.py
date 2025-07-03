#!/usr/bin/env python3
"""Quick test of the flake8 fixes."""

import subprocess


def test_flake8_fixes():
    """Test that flake8 errors are fixed."""
    files_to_check = [
        "scripts/build.py",
        "scripts/validate_package.py",
        "tests/test_exceptions.py",
        "tests/test_package_integration.py",
    ]

    for file in files_to_check:
        print(f"Checking {file}...")
        result = subprocess.run(
            ["python", "-m", "flake8", file], capture_output=True, text=True
        )

        if result.returncode == 0:
            print(f"✅ {file} - No flake8 errors")
        else:
            print(f"❌ {file} - Still has errors:")
            print(result.stdout)

    return True


if __name__ == "__main__":
    test_flake8_fixes()
