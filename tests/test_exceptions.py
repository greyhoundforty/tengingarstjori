"""Tests for custom exceptions."""

import pytest

from tengingarstjori.exceptions import (
    BackupError,
    CLIError,
    ConfigurationError,
    ConnectionError,
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
    """Test the base TengingarstjoriError exception."""
    error = TengingarstjoriError("Test error message")

    assert str(error) == "Test error message"
    assert error.message == "Test error message"
    assert error.details is None


def test_base_exception_with_details():
    """Test the base exception with details."""
    error = TengingarstjoriError("Test error", "Additional details")

    assert str(error) == "Test error: Additional details"
    assert error.message == "Test error"
    assert error.details == "Additional details"


def test_ssh_config_error():
    """Test SSH configuration error."""
    error = SSHConfigError("SSH config error")

    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "SSH config error"


def test_connection_error():
    """Test connection error."""
    error = ConnectionError("Connection failed")

    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "Connection failed"


def test_validation_error():
    """Test validation error with field information."""
    error = ValidationError("hostname", "invalid-host", "Invalid hostname format")

    assert isinstance(error, TengingarstjoriError)
    assert error.field == "hostname"
    assert error.value == "invalid-host"
    assert error.reason == "Invalid hostname format"
    assert "hostname" in str(error)
    assert "invalid-host" in str(error)
    assert "Invalid hostname format" in str(error)


def test_setup_error():
    """Test setup error."""
    error = SetupError("Setup failed")

    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "Setup failed"


def test_file_operation_error():
    """Test file operation error with context."""
    original_error = FileNotFoundError("File not found")
    error = FileOperationError("read", "/path/to/file", original_error)

    assert isinstance(error, TengingarstjoriError)
    assert error.operation == "read"
    assert error.path == "/path/to/file"
    assert error.original_error == original_error
    assert "read" in str(error)
    assert "/path/to/file" in str(error)


def test_key_discovery_error():
    """Test SSH key discovery error."""
    error = KeyDiscoveryError("Failed to discover SSH keys")

    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "Failed to discover SSH keys"


def test_cli_error():
    """Test CLI error with command context."""
    error = CLIError("add", "Invalid arguments", 2)

    assert isinstance(error, TengingarstjoriError)
    assert error.command == "add"
    assert error.exit_code == 2
    assert "add" in str(error)
    assert "Invalid arguments" in str(error)


def test_cli_error_default_exit_code():
    """Test CLI error with default exit code."""
    error = CLIError("list", "Command failed")

    assert error.exit_code == 1  # Default exit code


def test_configuration_error():
    """Test configuration error."""
    error = ConfigurationError("Invalid configuration")

    assert isinstance(error, TengingarstjoriError)
    assert str(error) == "Invalid configuration"


def test_permission_error():
    """Test permission error with resource context."""
    error = PermissionError("/etc/ssh/config", "write")

    assert isinstance(error, TengingarstjoriError)
    assert error.resource == "/etc/ssh/config"
    assert error.operation == "write"
    assert "write" in str(error)
    assert "/etc/ssh/config" in str(error)


def test_duplicate_connection_error():
    """Test duplicate connection error."""
    error = DuplicateConnectionError("my-server")

    assert isinstance(error, ConnectionError)
    assert isinstance(error, TengingarstjoriError)
    assert error.connection_name == "my-server"
    assert "my-server" in str(error)
    assert "already exists" in str(error)


def test_connection_not_found_error():
    """Test connection not found error."""
    error = ConnectionNotFoundError("my-server", "name")

    assert isinstance(error, ConnectionError)
    assert isinstance(error, TengingarstjoriError)
    assert error.identifier == "my-server"
    assert error.search_type == "name"
    assert "my-server" in str(error)
    assert "name" in str(error)


def test_connection_not_found_error_default_search_type():
    """Test connection not found error with default search type."""
    error = ConnectionNotFoundError("123")

    assert error.search_type == "name"  # Default search type


def test_invalid_ssh_key_error():
    """Test invalid SSH key error."""
    error = InvalidSSHKeyError("/path/to/key", "File not readable")

    assert isinstance(error, ValidationError)
    assert isinstance(error, TengingarstjoriError)
    assert error.key_path == "/path/to/key"
    assert error.field == "ssh_key"
    assert error.value == "/path/to/key"
    assert error.reason == "File not readable"


def test_backup_error():
    """Test backup error."""
    original_error = OSError("Permission denied")
    error = BackupError("/source/path", "/backup/path", original_error)

    assert isinstance(error, TengingarstjoriError)
    assert error.source_path == "/source/path"
    assert error.backup_path == "/backup/path"
    assert error.original_error == original_error
    assert "/source/path" in str(error)
    assert "/backup/path" in str(error)


def test_exception_hierarchy():
    """Test that exception hierarchy is correct."""
    # Test that all custom exceptions inherit from TengingarstjoriError
    exceptions_to_test = [
        (SSHConfigError, ("Test message",)),
        (ConnectionError, ("Test message",)),
        (ValidationError, ("field", "value", "reason")),
        (SetupError, ("Test message",)),
        (FileOperationError, ("read", "/path", Exception())),
        (KeyDiscoveryError, ("Test message",)),
        (CLIError, ("command", "Test message")),
        (ConfigurationError, ("Test message",)),
        (PermissionError, ("/resource", "operation")),
    ]

    for exception_class, args in exceptions_to_test:
        error = exception_class(*args)
        assert isinstance(error, TengingarstjoriError)
        assert isinstance(error, Exception)


def test_specialized_exception_hierarchy():
    """Test that specialized exceptions inherit from their parent classes."""
    # DuplicateConnectionError should inherit from ConnectionError
    error = DuplicateConnectionError("test")
    assert isinstance(error, ConnectionError)
    assert isinstance(error, TengingarstjoriError)

    # ConnectionNotFoundError should inherit from ConnectionError
    error = ConnectionNotFoundError("test")
    assert isinstance(error, ConnectionError)
    assert isinstance(error, TengingarstjoriError)

    # InvalidSSHKeyError should inherit from ValidationError
    error = InvalidSSHKeyError("/path", "reason")
    assert isinstance(error, ValidationError)
    assert isinstance(error, TengingarstjoriError)


def test_exception_catching():
    """Test that exceptions can be caught by their parent classes."""
    # Test catching specific exception
    with pytest.raises(DuplicateConnectionError):
        raise DuplicateConnectionError("test")

    # Test catching by parent class
    with pytest.raises(ConnectionError):
        raise DuplicateConnectionError("test")

    # Test catching by base class
    with pytest.raises(TengingarstjoriError):
        raise DuplicateConnectionError("test")

    # Test catching by Exception (use more specific exception)
    with pytest.raises(TengingarstjoriError):
        raise DuplicateConnectionError("test")


def test_exception_messages_are_informative():
    """Test that exception messages contain useful information."""
    # ValidationError should include field, value, and reason
    error = ValidationError("port", "99999", "Port out of range")
    message = str(error)
    assert "port" in message
    assert "99999" in message
    assert "Port out of range" in message

    # FileOperationError should include operation and path
    error = FileOperationError("write", "/tmp/test", Exception("Original error"))
    message = str(error)
    assert "write" in message
    assert "/tmp/test" in message

    # CLIError should include command name
    error = CLIError("init", "Initialization failed")
    message = str(error)
    assert "init" in message
    assert "Initialization failed" in message


def test_exception_attributes_are_accessible():
    """Test that custom exception attributes are accessible."""
    # ValidationError attributes
    error = ValidationError("field", "value", "reason")
    assert error.field == "field"
    assert error.value == "value"
    assert error.reason == "reason"

    # FileOperationError attributes
    original = Exception("test")
    error = FileOperationError("read", "/path", original)
    assert error.operation == "read"
    assert error.path == "/path"
    assert error.original_error == original

    # CLIError attributes
    error = CLIError("command", "message", 42)
    assert error.command == "command"
    assert error.exit_code == 42

    # DuplicateConnectionError attributes
    error = DuplicateConnectionError("conn-name")
    assert error.connection_name == "conn-name"

    # ConnectionNotFoundError attributes
    error = ConnectionNotFoundError("identifier", "search_type")
    assert error.identifier == "identifier"
    assert error.search_type == "search_type"
