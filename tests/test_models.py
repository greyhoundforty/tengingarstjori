"""Tests for SSH Connection models."""

from datetime import datetime

from tengingarstjori.models import SSHConnection


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


def test_ssh_config_block_with_hostname():
    """Test SSH config block with different hostname."""
    conn = SSHConnection(
        name="internal-server",
        host="internal.example.com",
        hostname="10.0.1.100",
        user="admin",
    )

    config_block = conn.to_ssh_config_block()

    assert "Host internal-server" in config_block
    assert "HostName 10.0.1.100" in config_block
    assert "User admin" in config_block


def test_ssh_config_block_with_proxy_jump():
    """Test SSH config block with ProxyJump."""
    conn = SSHConnection(
        name="behind-bastion",
        host="private.example.com",
        user="admin",
        proxy_jump="bastion.example.com",
    )

    config_block = conn.to_ssh_config_block()

    assert "Host behind-bastion" in config_block
    assert "ProxyJump bastion.example.com" in config_block


def test_ssh_config_block_with_port_forwarding():
    """Test SSH config block with port forwarding."""
    conn = SSHConnection(
        name="db-server",
        host="database.example.com",
        user="dbuser",
        local_forward="3306:localhost:3306",
        remote_forward="8080:localhost:8080",
    )

    config_block = conn.to_ssh_config_block()

    assert "Host db-server" in config_block
    assert "LocalForward 3306:localhost:3306" in config_block
    assert "RemoteForward 8080:localhost:8080" in config_block


def test_usage_update():
    """Test usage statistics update."""
    conn = SSHConnection(name="test-server", host="example.com", user="testuser")

    initial_count = conn.use_count
    initial_last_used = conn.last_used

    conn.update_usage()

    assert conn.use_count == initial_count + 1
    assert conn.last_used is not None
    assert conn.last_used != initial_last_used


def test_model_serialization():
    """Test model can be serialized and deserialized."""
    original_conn = SSHConnection(
        name="serialization-test",
        host="example.com",
        user="testuser",
        port=2222,
        identity_file="~/.ssh/test_key",
        proxy_jump="bastion.example.com",
        notes="Test serialization",
    )

    # Serialize to dict
    conn_dict = original_conn.model_dump()

    # Deserialize from dict
    restored_conn = SSHConnection(**conn_dict)

    assert restored_conn.name == original_conn.name
    assert restored_conn.host == original_conn.host
    assert restored_conn.user == original_conn.user
    assert restored_conn.port == original_conn.port
    assert restored_conn.identity_file == original_conn.identity_file
    assert restored_conn.proxy_jump == original_conn.proxy_jump
    assert restored_conn.notes == original_conn.notes
    assert restored_conn.id == original_conn.id


def test_connection_with_extra_options():
    """Test connection with extra SSH options."""
    conn = SSHConnection(
        name="extra-options-server",
        host="example.com",
        user="testuser",
        extra_options={
            "StrictHostKeyChecking": "no",
            "UserKnownHostsFile": "/dev/null",
            "ConnectTimeout": "30",
        },
    )

    config_block = conn.to_ssh_config_block()

    assert "StrictHostKeyChecking no" in config_block
    assert "UserKnownHostsFile /dev/null" in config_block
    assert "ConnectTimeout 30" in config_block


def test_connection_with_tags():
    """Test connection with organization tags."""
    conn = SSHConnection(
        name="tagged-server",
        host="example.com",
        user="testuser",
        tags=["production", "database", "critical"],
    )

    assert "production" in conn.tags
    assert "database" in conn.tags
    assert "critical" in conn.tags
    assert len(conn.tags) == 3


def test_default_port_not_in_config():
    """Test that default port 22 is not included in SSH config."""
    conn = SSHConnection(
        name="default-port-server",
        host="example.com",
        user="testuser",
        port=22,  # Default port
    )

    config_block = conn.to_ssh_config_block()

    assert "Port 22" not in config_block
    assert "Port" not in config_block


def test_custom_port_in_config():
    """Test that custom ports are included in SSH config."""
    conn = SSHConnection(
        name="custom-port-server",
        host="example.com",
        user="testuser",
        port=2222,  # Custom port
    )

    config_block = conn.to_ssh_config_block()

    assert "Port 2222" in config_block
