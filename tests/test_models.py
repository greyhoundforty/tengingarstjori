"""Tests for SSH Connection models."""

from datetime import datetime

from src.models import SSHConnection


def test_ssh_connection_creation():
    """Test basic SSH connection creation."""
    conn = SSHConnection(name="test-server", host="example.com", user="testuser")

    assert conn.name == "test-server"
    assert conn.host == "example.com"
    assert conn.user == "testuser"
    assert conn.port == 22  # default
    assert conn.use_count == 0
    assert conn.id is not None


def test_ssh_connection_with_options():
    """Test SSH connection with advanced options."""
    conn = SSHConnection(
        name="advanced-server",
        host="192.168.1.100",
        hostname="internal.example.com",
        user="admin",
        port=2222,
        identity_file="~/.ssh/special_key",
        proxy_jump="bastion.example.com",
        notes="Production server",
    )

    assert conn.hostname == "internal.example.com"
    assert conn.port == 2222
    assert conn.identity_file == "~/.ssh/special_key"
    assert conn.proxy_jump == "bastion.example.com"
    assert conn.notes == "Production server"


def test_ssh_config_block_generation():
    """Test SSH config block generation."""
    conn = SSHConnection(
        name="test-server",
        host="example.com",
        user="testuser",
        port=2222,
        identity_file="~/.ssh/id_rsa",
        notes="Test connection",
    )

    config_block = conn.to_ssh_config_block()

    assert "Host test-server" in config_block
    assert "HostName example.com" in config_block
    assert "User testuser" in config_block
    assert "Port 2222" in config_block
    assert "IdentityFile ~/.ssh/id_rsa" in config_block
    assert "# Test connection" in config_block


def test_usage_update():
    """Test usage statistics update."""
    conn = SSHConnection(name="test-server", host="example.com", user="testuser")

    assert conn.use_count == 0
    assert conn.last_used is None

    conn.update_usage()

    assert conn.use_count == 1
    assert conn.last_used is not None
    assert isinstance(conn.last_used, datetime)


def test_unique_ids():
    """Test that each connection gets a unique ID."""
    conn1 = SSHConnection(name="server1", host="host1", user="user1")
    conn2 = SSHConnection(name="server2", host="host2", user="user2")

    assert conn1.id != conn2.id
