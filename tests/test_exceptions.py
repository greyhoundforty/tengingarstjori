"""Tests for custom exception classes."""

import pytest

from src.exceptions import (
    BackupError,
    CLIError,
    ConfigurationError,
    ConnectionNotFoundError,
    DuplicateConnectionError,
    FileOperationError,
    InvalidSSHKeyError,
    KeyDiscoveryError,
    PermissionError,
    SetupError,
    SSHConfigError,
    TengingarstjoriError,
    ValidationError,
)


def test_base_exception():
    """Test the base TengingarstjoriError."""
    # Test with just message
    error = TengingarstjoriError("Base error")
    assert str(error) == "Base error"
    assert error.message == "Base error"
    assert error.details is None

    # Test with message and details
    error_with_details = TengingarstjoriError("Base error", "Additional details")
    assert str(error_with_details) == "Base error: Additional details"
    assert error_with_details.details == "Additional details"


def test_ssh_config_error():
    """Test SSHConfigError."""
    error = SSHConfigError("SSH config failed")
    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "SSH config failed"


def test_validation_error():
    """Test ValidationError with field details."""
    error = ValidationError("port", "99999", "Port out of range")
    assert isinstance(error, TengingarstjoriError)
    assert error.field == "port"
    assert error.value == "99999"
    assert error.reason == "Port out of range"
    assert "port" in str(error)
    assert "99999" in str(error)
    assert "Port out of range" in str(error)


def test_setup_error():
    """Test SetupError."""
    error = SetupError("Setup failed")
    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "Setup failed"


def test_file_operation_error():
    """Test FileOperationError with context."""
    original_error = OSError("Permission denied")
    error = FileOperationError("write", "/path/to/file", original_error)

    assert isinstance(error, TengingarstjoriError)
    assert error.operation == "write"
    assert error.path == "/path/to/file"
    assert error.original_error == original_error
    assert "write" in str(error)
    assert "/path/to/file" in str(error)


def test_key_discovery_error():
    """Test KeyDiscoveryError."""
    error = KeyDiscoveryError("No keys found")
    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "No keys found"


def test_cli_error():
    """Test CLIError with command context."""
    error = CLIError("add", "Invalid arguments", 2)
    assert isinstance(error, TengingarstjoriError)
    assert error.command == "add"
    assert error.exit_code == 2
    assert "add" in str(error)
    assert "Invalid arguments" in str(error)


def test_configuration_error():
    """Test ConfigurationError."""
    error = ConfigurationError("Invalid config")
    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "Invalid config"


def test_permission_error():
    """Test PermissionError with resource context."""
    error = PermissionError("/path/to/file", "read")
    assert isinstance(error, TengingarstjoriError)
    assert error.resource == "/path/to/file"
    assert error.operation == "read"
    assert "Permission denied" in str(error)
    assert "/path/to/file" in str(error)


def test_duplicate_connection_error():
    """Test DuplicateConnectionError."""
    error = DuplicateConnectionError("web-server")
    assert isinstance(error, TengingarstjoriError)
    assert error.connection_name == "web-server"
    assert "web-server" in str(error)
    assert "already exists" in str(error)


def test_connection_not_found_error():
    """Test ConnectionNotFoundError."""
    # Test with default search type
    error = ConnectionNotFoundError("web-server")
    assert isinstance(error, TengingarstjoriError)
    assert error.identifier == "web-server"
    assert error.search_type == "name"
    assert "web-server" in str(error)
    assert "name" in str(error)

    # Test with specific search type
    error_by_id = ConnectionNotFoundError("12345", "id")
    assert error_by_id.search_type == "id"
    assert "id" in str(error_by_id)


def test_invalid_ssh_key_error():
    """Test InvalidSSHKeyError."""
    error = InvalidSSHKeyError("/path/to/key", "File not found")
    assert isinstance(error, ValidationError)
    assert isinstance(error, TengingarstjoriError)
    assert error.key_path == "/path/to/key"
    assert error.field == "ssh_key"
    assert error.value == "/path/to/key"
    assert error.reason == "File not found"


def test_backup_error():
    """Test BackupError."""
    original_error = OSError("Disk full")
    error = BackupError("/source/path", "/backup/path", original_error)

    assert isinstance(error, TengingarstjoriError)
    assert error.source_path == "/source/path"
    assert error.backup_path == "/backup/path"
    assert error.original_error == original_error
    assert "/source/path" in str(error)
    assert "/backup/path" in str(error)


def test_exception_inheritance():
    """Test that all exceptions properly inherit from TengingarstjoriError."""
    exceptions_to_test = [
        SSHConfigError("test"),
        ValidationError("field", "value", "reason"),
        SetupError("test"),
        FileOperationError("op", "path", Exception("test")),
        KeyDiscoveryError("test"),
        CLIError("cmd", "msg"),
        ConfigurationError("test"),
        PermissionError("resource", "op"),
        DuplicateConnectionError("name"),
        ConnectionNotFoundError("id"),
        InvalidSSHKeyError("path", "reason"),
        BackupError("src", "dst", Exception("test")),
    ]

    for exception in exceptions_to_test:
        assert isinstance(exception, TengingarstjoriError)
        assert isinstance(exception, Exception)
