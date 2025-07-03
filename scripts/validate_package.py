#!/usr/bin/env python3
"""
Test script to validate the Tengingarstjóri package.

This script performs basic validation of the package structure and functionality.
"""

import sys
import tempfile
from pathlib import Path


def test_imports():
    """Test that all main modules can be imported."""
    print("🔍 Testing imports...")

    try:
        # Test main package import
        import tengingarstjori

        print(
            f"✅ Main package imported successfully (version: {tengingarstjori.__version__})"
        )

        # Test individual module imports
        from tengingarstjori import SSHConfigManager, SSHConnection, cli

        print("✅ Individual modules imported successfully")

        # Test exception imports
        from tengingarstjori.exceptions import TengingarstjoriError

        print("✅ Exception classes imported successfully")

        # Test that imports are actually usable
        assert SSHConnection is not None
        assert SSHConfigManager is not None
        assert cli is not None
        assert TengingarstjoriError is not None

        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_model_creation():
    """Test that models can be created and used."""
    print("\n🔍 Testing model creation...")

    try:
        from tengingarstjori import SSHConnection

        # Create a basic connection
        conn = SSHConnection(name="test-server", host="example.com", user="testuser")

        # Test basic attributes
        assert conn.name == "test-server"
        assert conn.host == "example.com"
        assert conn.user == "testuser"
        assert conn.port == 22  # Default port

        # Test SSH config generation
        config_block = conn.to_ssh_config_block()
        assert "Host test-server" in config_block
        assert "HostName example.com" in config_block
        assert "User testuser" in config_block

        print("✅ Model creation and basic functionality works")
        return True

    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False


def test_config_manager():
    """Test that config manager can be created and used."""
    print("\n🔍 Testing config manager...")

    try:
        from tengingarstjori import SSHConfigManager, SSHConnection

        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)

            # Create config manager
            manager = SSHConfigManager(config_dir=config_dir)

            # Test basic operations
            assert len(manager.list_connections()) == 0

            # Add a connection
            conn = SSHConnection(
                name="test-connection", host="test.example.com", user="testuser"
            )

            result = manager.add_connection(conn)
            assert result is True

            # Test retrieval
            connections = manager.list_connections()
            assert len(connections) == 1
            assert connections[0].name == "test-connection"

            # Test get by name
            retrieved = manager.get_connection_by_name("test-connection")
            assert retrieved is not None
            assert retrieved.name == "test-connection"

        print("✅ Config manager functionality works")
        return True

    except Exception as e:
        print(f"❌ Config manager test failed: {e}")
        return False


def test_cli_accessibility():
    """Test that CLI is accessible."""
    print("\n🔍 Testing CLI accessibility...")

    try:
        from tengingarstjori import cli

        # Test that CLI function exists
        assert callable(cli)

        # Test that CLI has proper structure (Click command)
        assert hasattr(cli, "commands")

        print("✅ CLI is accessible and properly structured")
        return True

    except Exception as e:
        print(f"❌ CLI accessibility test failed: {e}")
        return False


def test_package_metadata():
    """Test that package metadata is properly defined."""
    print("\n🔍 Testing package metadata...")

    try:
        import tengingarstjori

        # Check version
        assert hasattr(tengingarstjori, "__version__")
        assert isinstance(tengingarstjori.__version__, str)
        assert len(tengingarstjori.__version__) > 0

        # Check author
        assert hasattr(tengingarstjori, "__author__")
        assert isinstance(tengingarstjori.__author__, str)

        # Check description
        assert hasattr(tengingarstjori, "__description__")
        assert isinstance(tengingarstjori.__description__, str)

        # Check __all__ exports
        assert hasattr(tengingarstjori, "__all__")
        assert isinstance(tengingarstjori.__all__, list)
        assert len(tengingarstjori.__all__) > 0

        print("✅ Package metadata is properly defined")
        return True

    except Exception as e:
        print(f"❌ Package metadata test failed: {e}")
        return False


def test_exceptions():
    """Test that custom exceptions work properly."""
    print("\n🔍 Testing custom exceptions...")

    try:
        from tengingarstjori.exceptions import (
            ConnectionError,
            DuplicateConnectionError,
            TengingarstjoriError,
            ValidationError,
        )

        # Test base exception
        base_error = TengingarstjoriError("Test error")
        assert str(base_error) == "Test error"

        # Test inheritance
        conn_error = ConnectionError("Connection failed")
        assert isinstance(conn_error, TengingarstjoriError)

        # Test specialized exception
        dup_error = DuplicateConnectionError("test-conn")
        assert isinstance(dup_error, ConnectionError)
        assert isinstance(dup_error, TengingarstjoriError)
        assert "test-conn" in str(dup_error)

        # Test validation error
        val_error = ValidationError("host", "invalid", "Invalid format")
        assert val_error.field == "host"
        assert val_error.value == "invalid"
        assert val_error.reason == "Invalid format"

        print("✅ Custom exceptions work properly")
        return True

    except Exception as e:
        print(f"❌ Exception test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("🧪 Running Tengingarstjóri Package Validation\n")

    tests = [
        test_imports,
        test_model_creation,
        test_config_manager,
        test_cli_accessibility,
        test_package_metadata,
        test_exceptions,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1

    print(f"\n{'=' * 50}")
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Package is ready for distribution.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before distribution.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
