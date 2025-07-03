"""Tests for SSH Config Manager."""

import tempfile
from pathlib import Path

import pytest

from tengingarstjori.config_manager import SSHConfigManager
from tengingarstjori.models import SSHConnection


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def config_manager(temp_config_dir):
    """Create a config manager with temporary directory."""
    return SSHConfigManager(config_dir=temp_config_dir)


@pytest.fixture
def sample_connection():
    """Create a sample SSH connection for testing."""
    return SSHConnection(
        name="test-server",
        host="example.com",
        user="testuser",
        port=2222,
        identity_file="~/.ssh/test_key",
        notes="Test connection",
    )


def test_config_manager_initialization(config_manager):
    """Test config manager initializes correctly."""
    assert config_manager.config_dir.exists()
    assert config_manager.connections == []
    assert config_manager.settings == {}


def test_add_connection(config_manager, sample_connection):
    """Test adding a new connection."""
    result = config_manager.add_connection(sample_connection)

    assert result is True
    assert len(config_manager.connections) == 1
    assert config_manager.connections[0].name == "test-server"


def test_add_duplicate_connection(config_manager, sample_connection):
    """Test adding a duplicate connection fails."""
    config_manager.add_connection(sample_connection)

    # Try to add the same connection again
    duplicate_connection = SSHConnection(
        name="test-server",  # Same name
        host="different.com",
        user="different",
    )

    result = config_manager.add_connection(duplicate_connection)

    assert result is False
    assert len(config_manager.connections) == 1


def test_get_connection_by_name(config_manager, sample_connection):
    """Test retrieving connection by name."""
    config_manager.add_connection(sample_connection)

    found_connection = config_manager.get_connection_by_name("test-server")

    assert found_connection is not None
    assert found_connection.name == "test-server"
    assert found_connection.host == "example.com"


def test_get_connection_by_name_not_found(config_manager):
    """Test retrieving non-existent connection returns None."""
    result = config_manager.get_connection_by_name("non-existent")

    assert result is None


def test_get_connection_by_id(config_manager, sample_connection):
    """Test retrieving connection by ID."""
    config_manager.add_connection(sample_connection)

    found_connection = config_manager.get_connection(sample_connection.id)

    assert found_connection is not None
    assert found_connection.id == sample_connection.id
    assert found_connection.name == "test-server"


def test_list_connections(config_manager):
    """Test listing all connections."""
    # Add multiple connections
    conn1 = SSHConnection(name="server1", host="host1.com", user="user1")
    conn2 = SSHConnection(name="server2", host="host2.com", user="user2")

    config_manager.add_connection(conn1)
    config_manager.add_connection(conn2)

    connections = config_manager.list_connections()

    assert len(connections) == 2
    assert connections[0].name == "server1"
    assert connections[1].name == "server2"


def test_remove_connection(config_manager, sample_connection):
    """Test removing a connection."""
    config_manager.add_connection(sample_connection)

    result = config_manager.remove_connection(sample_connection.id)

    assert result is True
    assert len(config_manager.connections) == 0


def test_remove_non_existent_connection(config_manager):
    """Test removing non-existent connection returns False."""
    result = config_manager.remove_connection("non-existent-id")

    assert result is False


def test_update_connection(config_manager, sample_connection):
    """Test updating an existing connection."""
    config_manager.add_connection(sample_connection)

    # Update the connection
    sample_connection.notes = "Updated notes"
    sample_connection.port = 3333

    result = config_manager.update_connection(sample_connection)

    assert result is True

    # Verify the update
    updated_connection = config_manager.get_connection(sample_connection.id)
    assert updated_connection.notes == "Updated notes"
    assert updated_connection.port == 3333


def test_update_non_existent_connection(config_manager):
    """Test updating non-existent connection returns False."""
    non_existent_conn = SSHConnection(
        name="non-existent",
        host="example.com",
        user="user",
    )

    result = config_manager.update_connection(non_existent_conn)

    assert result is False


def test_settings_management(config_manager):
    """Test settings management."""
    # Test setting a value
    config_manager.update_setting("test_key", "test_value")

    # Test getting the value
    value = config_manager.get_setting("test_key")
    assert value == "test_value"

    # Test getting non-existent value with default
    default_value = config_manager.get_setting("non_existent", "default")
    assert default_value == "default"


def test_initialization_status(config_manager):
    """Test initialization status management."""
    # Should not be initialized initially
    assert not config_manager.is_initialized()

    # Mark as initialized
    config_manager.mark_initialized()

    # Should now be initialized
    assert config_manager.is_initialized()


def test_discover_ssh_keys(config_manager, temp_config_dir):
    """Test SSH key discovery."""
    # Create a mock SSH directory with test keys
    ssh_dir = temp_config_dir / ".ssh"
    ssh_dir.mkdir()

    # Create some test key files
    (ssh_dir / "id_rsa").write_text(
        "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----"
    )
    (ssh_dir / "id_ed25519").write_text(
        "-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----"
    )

    # Update the config manager to use our test SSH directory
    config_manager.ssh_dir = ssh_dir

    discovered_keys = config_manager.discover_ssh_keys()

    assert len(discovered_keys) >= 2
    assert any("id_rsa" in key for key in discovered_keys)
    assert any("id_ed25519" in key for key in discovered_keys)


def test_persistence(config_manager, sample_connection):
    """Test that connections persist across manager instances."""
    # Add connection to first manager
    config_manager.add_connection(sample_connection)

    # Create new manager with same config directory
    new_manager = SSHConfigManager(config_dir=config_manager.config_dir)

    # Should load the previously saved connection
    assert len(new_manager.connections) == 1
    assert new_manager.connections[0].name == "test-server"


def test_settings_persistence(config_manager):
    """Test that settings persist across manager instances."""
    # Set a setting in first manager
    config_manager.update_setting("test_setting", "test_value")

    # Create new manager with same config directory
    new_manager = SSHConfigManager(config_dir=config_manager.config_dir)

    # Should load the previously saved setting
    assert new_manager.get_setting("test_setting") == "test_value"


def test_ssh_config_file_creation(config_manager, sample_connection):
    """Test that SSH config files are created properly."""
    config_manager.add_connection(sample_connection)

    # Check that managed config file exists
    assert config_manager.managed_config.exists()

    # Read the managed config content
    with open(config_manager.managed_config, "r") as f:
        content = f.read()

    # Should contain our connection
    assert "Host test-server" in content
    assert "HostName example.com" in content
    assert "User testuser" in content
    assert "Port 2222" in content
    assert "IdentityFile ~/.ssh/test_key" in content
    assert "# Test connection" in content
