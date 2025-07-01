"""Test basic functionality after Phase 1 fixes."""

import pytest

from src.exceptions import (
    ConnectionError,
    DuplicateConnectionError,
    SSHConfigError,
    TengingarstjoriError,
    ValidationError,
)
from src.models import SSHConnection


def test_exception_hierarchy():
    """Test that custom exceptions work correctly."""
    # Test base exception
    base_error = TengingarstjoriError("Base error", "Additional details")
    assert str(base_error) == "Base error: Additional details"

    # Test SSH config error
    ssh_error = SSHConfigError("SSH config failed")
    assert isinstance(ssh_error, TengingarstjoriError)
    assert str(ssh_error) == "SSH config failed"

    # Test connection error
    conn_error = ConnectionError("Connection failed")
    assert isinstance(conn_error, TengingarstjoriError)

    # Test duplicate connection error
    dup_error = DuplicateConnectionError("test-server")
    assert isinstance(dup_error, ConnectionError)
    assert "test-server" in str(dup_error)
    assert "already exists" in str(dup_error)

    # Test validation error
    val_error = ValidationError("port", "99999", "Port out of range")
    assert isinstance(val_error, TengingarstjoriError)
    assert "port" in str(val_error)
    assert "99999" in str(val_error)


def test_ssh_connection_creation():
    """Test that SSH connection models still work after changes."""
    conn = SSHConnection(
        name="test-server", host="example.com", user="testuser", port=22
    )

    assert conn.name == "test-server"
    assert conn.host == "example.com"
    assert conn.user == "testuser"
    assert conn.port == 22
    assert conn.use_count == 0
    assert conn.id is not None


def test_ssh_connection_config_generation():
    """Test SSH config block generation."""
    conn = SSHConnection(
        name="web-server",
        host="192.168.1.10",
        user="deploy",
        port=2222,
        identity_file="~/.ssh/id_ed25519",
        notes="Production web server",
    )

    config_block = conn.to_ssh_config_block()

    assert "Host web-server" in config_block
    assert "HostName 192.168.1.10" in config_block
    assert "User deploy" in config_block
    assert "Port 2222" in config_block
    assert "IdentityFile ~/.ssh/id_ed25519" in config_block
    assert "# Production web server" in config_block


def test_import_statements():
    """Test that all modules can be imported without errors."""
    # Test imports work
    from src.cli import cli
    from src.config_manager import SSHConfigManager
    from src.exceptions import TengingarstjoriError
    from src.models import SSHConnection
    from src.setup import SetupWizard, run_initial_setup

    # Basic functionality test
    assert SSHConnection is not None
    assert SSHConfigManager is not None
    assert cli is not None
    assert run_initial_setup is not None
    assert SetupWizard is not None
    assert TengingarstjoriError is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
