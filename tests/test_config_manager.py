"""
Tests for SSH Config Manager
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.config_manager import SSHConfigManager
from src.models import SSHConnection


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def config_manager(temp_config_dir):
    """Create a config manager with temporary directory"""
    return SSHConfigManager(config_dir=temp_config_dir)


def test_config_manager_initialization(config_manager, temp_config_dir):
    """Test config manager initialization"""
    assert config_manager.config_dir == temp_config_dir
    assert config_manager.config_dir.exists()
    assert len(config_manager.connections) == 0


def test_add_connection(config_manager):
    """Test adding a connection"""
    conn = SSHConnection(
        name="test-server",
        host="example.com",
        user="testuser"
    )
    
    result = config_manager.add_connection(conn)
    assert result is True
    assert len(config_manager.connections) == 1
    assert config_manager.connections[0].name == "test-server"


def test_add_duplicate_connection(config_manager):
    """Test adding a connection with duplicate name"""
    conn1 = SSHConnection(name="server", host="host1", user="user1")
    conn2 = SSHConnection(name="server", host="host2", user="user2")
    
    assert config_manager.add_connection(conn1) is True
    assert config_manager.add_connection(conn2) is False  # Should fail
    assert len(config_manager.connections) == 1


def test_remove_connection(config_manager):
    """Test removing a connection"""
    conn = SSHConnection(name="test-server", host="example.com", user="testuser")
    config_manager.add_connection(conn)
    
    assert len(config_manager.connections) == 1
    
    result = config_manager.remove_connection(conn.id)
    assert result is True
    assert len(config_manager.connections) == 0


def test_get_connection_by_name(config_manager):
    """Test getting connection by name"""
    conn = SSHConnection(name="test-server", host="example.com", user="testuser")
    config_manager.add_connection(conn)
    
    found_conn = config_manager.get_connection_by_name("test-server")
    assert found_conn is not None
    assert found_conn.name == "test-server"
    
    not_found = config_manager.get_connection_by_name("nonexistent")
    assert not_found is None


def test_settings_management(config_manager):
    """Test settings management"""
    # Test setting and getting
    config_manager.update_setting("test_key", "test_value")
    assert config_manager.get_setting("test_key") == "test_value"
    
    # Test default value
    assert config_manager.get_setting("nonexistent", "default") == "default"
    
    # Test initialization tracking
    assert not config_manager.is_initialized()
    config_manager.mark_initialized()
    assert config_manager.is_initialized()


def test_persistence(config_manager):
    """Test that connections and settings persist"""
    # Add connection and setting
    conn = SSHConnection(name="persist-test", host="example.com", user="testuser")
    config_manager.add_connection(conn)
    config_manager.update_setting("persist_test", "value")
    
    # Create new manager with same config dir
    new_manager = SSHConfigManager(config_dir=config_manager.config_dir)
    
    # Verify data persisted
    assert len(new_manager.connections) == 1
    assert new_manager.connections[0].name == "persist-test"
    assert new_manager.get_setting("persist_test") == "value"
