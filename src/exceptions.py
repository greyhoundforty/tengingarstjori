"""
Custom exception classes for Tengingarstjóri SSH Connection Manager.

This module defines a hierarchy of custom exceptions to provide better
error handling and more specific error messages throughout the application.
"""

from typing import Optional


class TengingarstjoriError(Exception):
    """
    Base exception class for all Tengingarstjóri-related errors.

    This serves as the parent class for all custom exceptions in the application,
    allowing for catch-all exception handling when needed.
    """

    def __init__(self, message: str, details: Optional[str] = None):
        """
        Initialize the base exception.

        Args:
            message: The main error message
            details: Optional additional details about the error
        """
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class SSHConfigError(TengingarstjoriError):
    """
    Exception raised for SSH configuration-related errors.

    This includes errors in reading, writing, or validating SSH configuration files.
    """

    pass


class ConnectionError(TengingarstjoriError):
    """
    Exception raised for SSH connection management errors.

    This includes errors in adding, removing, updating, or validating connections.
    """

    pass


class ValidationError(TengingarstjoriError):
    """
    Exception raised for data validation errors.

    This includes errors in validating connection parameters, configuration values,
    or any other input data.
    """

    def __init__(self, field: str, value: str, reason: str):
        """
        Initialize a validation error with specific field information.

        Args:
            field: The name of the field that failed validation
            value: The value that failed validation
            reason: The reason why validation failed
        """
        self.field = field
        self.value = value
        self.reason = reason
        message = (
            f"Validation failed for field '{field}' with value '{value}': {reason}"
        )
        super().__init__(message)


class SetupError(TengingarstjoriError):
    """
    Exception raised during initial setup process.

    This includes errors in discovering SSH keys, setting up configuration,
    or any other setup-related operations.
    """

    pass


class FileOperationError(TengingarstjoriError):
    """
    Exception raised for file system operation errors.

    This includes errors in reading, writing, creating, or deleting files
    and directories.
    """

    def __init__(self, operation: str, path: str, original_error: Exception):
        """
        Initialize a file operation error with context.

        Args:
            operation: The operation that failed (e.g., "read", "write", "create")
            path: The file path involved in the operation
            original_error: The original exception that caused the failure
        """
        self.operation = operation
        self.path = path
        self.original_error = original_error
        message = f"Failed to {operation} file '{path}'"
        super().__init__(message, str(original_error))


class KeyDiscoveryError(TengingarstjoriError):
    """
    Exception raised when SSH key discovery fails.

    This includes errors in scanning for SSH keys, validating key files,
    or accessing the SSH directory.
    """

    pass


class CLIError(TengingarstjoriError):
    """
    Exception raised for CLI-specific errors.

    This includes errors in command line argument parsing, user input validation,
    or CLI command execution.
    """

    def __init__(self, command: str, message: str, exit_code: int = 1):
        """
        Initialize a CLI error with command context.

        Args:
            command: The CLI command that failed
            message: The error message
            exit_code: The suggested exit code for the CLI
        """
        self.command = command
        self.exit_code = exit_code
        super().__init__(f"Command '{command}' failed: {message}")


class ConfigurationError(TengingarstjoriError):
    """
    Exception raised for configuration-related errors.

    This includes errors in loading, saving, or validating application configuration.
    """

    pass


class PermissionError(TengingarstjoriError):
    """
    Exception raised for permission-related errors.

    This includes errors when the application lacks necessary permissions
    to perform file operations or access resources.
    """

    def __init__(self, resource: str, operation: str):
        """
        Initialize a permission error with resource context.

        Args:
            resource: The resource that couldn't be accessed
            operation: The operation that was attempted
        """
        self.resource = resource
        self.operation = operation
        message = f"Permission denied: cannot {operation} {resource}"
        super().__init__(message)


class DuplicateConnectionError(ConnectionError):
    """Exception raised when attempting to create a connection with a duplicate name."""

    def __init__(self, connection_name: str):
        """
        Initialize a duplicate connection error.

        Args:
            connection_name: The name of the duplicate connection
        """
        self.connection_name = connection_name
        message = f"Connection with name '{connection_name}' already exists"
        super().__init__(message)


class ConnectionNotFoundError(ConnectionError):
    """Exception raised when a requested connection cannot be found."""

    def __init__(self, identifier: str, search_type: str = "name"):
        """
        Initialize a connection not found error.

        Args:
            identifier: The identifier used to search for the connection
            search_type: The type of identifier (e.g., "name", "id", "index")
        """
        self.identifier = identifier
        self.search_type = search_type
        message = f"Connection not found with {search_type}: '{identifier}'"
        super().__init__(message)


class InvalidSSHKeyError(ValidationError):
    """Exception raised when an SSH key file is invalid or inaccessible."""

    def __init__(self, key_path: str, reason: str):
        """
        Initialize an invalid SSH key error.

        Args:
            key_path: The path to the invalid SSH key
            reason: The reason why the key is invalid
        """
        self.key_path = key_path
        super().__init__("ssh_key", key_path, reason)


class BackupError(TengingarstjoriError):
    """
    Exception raised when backup operations fail.

    This includes errors in creating backups of SSH configuration files
    before making modifications.
    """

    def __init__(self, source_path: str, backup_path: str, original_error: Exception):
        """
        Initialize a backup error.

        Args:
            source_path: The path of the file being backed up
            backup_path: The intended backup file path
            original_error: The original exception that caused the backup to fail
        """
        self.source_path = source_path
        self.backup_path = backup_path
        self.original_error = original_error
        message = f"Failed to backup '{source_path}' to '{backup_path}'"
        super().__init__(message, str(original_error))
