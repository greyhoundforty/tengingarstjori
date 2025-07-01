"""Additional tests for SSH Connection models to improve coverage."""

from datetime import datetime

import pytest

from src.models import SSHConnection


class TestSSHConnectionAdvanced:
    """Advanced tests for SSH Connection model."""

    def test_ssh_connection_with_all_fields(self):
        """Test SSH connection with all possible fields."""
        now = datetime.now()
        conn = SSHConnection(
            name="full-test",
            host="example.com",
            hostname="actual.example.com",
            port=2222,
            user="testuser",
            identity_file="~/.ssh/special_key",
            proxy_jump="bastion.example.com",
            local_forward="8080:localhost:8080",
            remote_forward="9090:localhost:9090",
            extra_options={
                "StrictHostKeyChecking": "no",
                "UserKnownHostsFile": "/dev/null",
            },
            notes="Full featured connection",
            tags=["production", "web"],
            created_at=now,
            last_used=now,
            use_count=5,
        )

        assert conn.name == "full-test"
        assert conn.host == "example.com"
        assert conn.hostname == "actual.example.com"
        assert conn.port == 2222
        assert conn.user == "testuser"
        assert conn.identity_file == "~/.ssh/special_key"
        assert conn.proxy_jump == "bastion.example.com"
        assert conn.local_forward == "8080:localhost:8080"
        assert conn.remote_forward == "9090:localhost:9090"
        assert conn.extra_options["StrictHostKeyChecking"] == "no"
        assert conn.notes == "Full featured connection"
        assert conn.tags == ["production", "web"]
        assert conn.created_at == now
        assert conn.last_used == now
        assert conn.use_count == 5

    def test_ssh_config_block_with_hostname(self):
        """Test SSH config block generation when hostname differs from host."""
        conn = SSHConnection(
            name="hostname-test",
            host="192.168.1.10",
            hostname="actual-server.internal",
            user="testuser",
            port=22,
        )

        config_block = conn.to_ssh_config_block()

        assert "Host hostname-test" in config_block
        assert "HostName actual-server.internal" in config_block
        assert "192.168.1.10" not in config_block  # Should use hostname, not host

    def test_ssh_config_block_without_hostname(self):
        """Test SSH config block generation without separate hostname."""
        conn = SSHConnection(
            name="simple-test",
            host="simple.example.com",
            user="testuser",
        )

        config_block = conn.to_ssh_config_block()

        assert "Host simple-test" in config_block
        assert "HostName simple.example.com" in config_block

    def test_ssh_config_block_with_non_standard_port(self):
        """Test SSH config block generation with non-standard port."""
        conn = SSHConnection(
            name="port-test",
            host="example.com",
            user="testuser",
            port=2222,
        )

        config_block = conn.to_ssh_config_block()

        assert "Port 2222" in config_block

    def test_ssh_config_block_with_standard_port(self):
        """Test SSH config block generation with standard port (should be omitted)."""
        conn = SSHConnection(
            name="standard-port",
            host="example.com",
            user="testuser",
            port=22,
        )

        config_block = conn.to_ssh_config_block()

        assert "Port 22" not in config_block  # Standard port should not be included

    def test_ssh_config_block_with_all_advanced_options(self):
        """Test SSH config block with all advanced options."""
        conn = SSHConnection(
            name="advanced-test",
            host="example.com",
            user="testuser",
            identity_file="~/.ssh/special_key",
            proxy_jump="bastion.example.com",
            local_forward="8080:localhost:8080",
            remote_forward="9090:localhost:9090",
            extra_options={
                "StrictHostKeyChecking": "no",
                "UserKnownHostsFile": "/dev/null",
            },
            notes="Advanced connection with all options",
        )

        config_block = conn.to_ssh_config_block()

        assert "Host advanced-test" in config_block
        assert "HostName example.com" in config_block
        assert "User testuser" in config_block
        assert "IdentityFile ~/.ssh/special_key" in config_block
        assert "ProxyJump bastion.example.com" in config_block
        assert "LocalForward 8080:localhost:8080" in config_block
        assert "RemoteForward 9090:localhost:9090" in config_block
        assert "StrictHostKeyChecking no" in config_block
        assert "UserKnownHostsFile /dev/null" in config_block
        assert "# Advanced connection with all options" in config_block

    def test_ssh_config_block_notes_placement(self):
        """Test that notes are placed correctly in config block."""
        conn = SSHConnection(
            name="notes-test",
            host="example.com",
            user="testuser",
            notes="This is a test note",
        )

        config_block = conn.to_ssh_config_block()
        lines = config_block.split("\n")

        # Notes should be the second line (after Host line)
        assert lines[0] == "Host notes-test"
        assert lines[1] == "    # This is a test note"
        assert lines[2] == "    HostName example.com"

    def test_ssh_config_block_without_optional_fields(self):
        """Test SSH config block with minimal required fields only."""
        conn = SSHConnection(
            name="minimal",
            host="minimal.com",
            user="minuser",
        )

        config_block = conn.to_ssh_config_block()

        # Should not contain optional fields
        assert "IdentityFile" not in config_block
        assert "ProxyJump" not in config_block
        assert "LocalForward" not in config_block
        assert "RemoteForward" not in config_block
        assert "Port" not in config_block  # Port 22 should be omitted
        assert "#" not in config_block  # No notes

        # Should contain required fields
        assert "Host minimal" in config_block
        assert "HostName minimal.com" in config_block
        assert "User minuser" in config_block

    def test_update_usage_increments_correctly(self):
        """Test that update_usage increments use_count correctly."""
        conn = SSHConnection(name="usage-test", host="example.com", user="testuser")

        assert conn.use_count == 0
        assert conn.last_used is None

        # First usage
        conn.update_usage()
        assert conn.use_count == 1
        assert conn.last_used is not None
        first_usage = conn.last_used

        # Second usage (should increment)
        conn.update_usage()
        assert conn.use_count == 2
        assert conn.last_used != first_usage  # Should be updated

    def test_model_serialization_with_datetime(self):
        """Test model serialization handles datetime correctly."""
        now = datetime.now()
        conn = SSHConnection(
            name="serialize-test",
            host="example.com",
            user="testuser",
            created_at=now,
            last_used=now,
        )

        # Should be able to serialize to dict
        data = conn.model_dump()
        assert isinstance(data, dict)
        assert data["name"] == "serialize-test"
        assert "created_at" in data
        assert "last_used" in data

        # Should be able to recreate from dict
        restored_conn = SSHConnection(**data)
        assert restored_conn.name == conn.name
        assert restored_conn.host == conn.host
        assert restored_conn.user == conn.user

    def test_default_field_values(self):
        """Test that default field values are set correctly."""
        conn = SSHConnection(name="defaults", host="example.com", user="testuser")

        # Test default values
        assert conn.port == 22
        assert conn.hostname is None
        assert conn.identity_file is None
        assert conn.proxy_jump is None
        assert conn.local_forward is None
        assert conn.remote_forward is None
        assert conn.extra_options == {}
        assert conn.notes is None
        assert conn.tags == []
        assert conn.use_count == 0
        assert conn.last_used is None
        assert isinstance(conn.created_at, datetime)
        assert len(conn.id) > 0  # Should have a UUID

    def test_extra_options_in_config_block(self):
        """Test that extra_options are properly included in config block."""
        conn = SSHConnection(
            name="extra-test",
            host="example.com",
            user="testuser",
            extra_options={
                "ServerAliveInterval": "60",
                "ServerAliveCountMax": "3",
                "TCPKeepAlive": "yes",
            },
        )

        config_block = conn.to_ssh_config_block()

        assert "ServerAliveInterval 60" in config_block
        assert "ServerAliveCountMax 3" in config_block
        assert "TCPKeepAlive yes" in config_block

    def test_empty_extra_options(self):
        """Test that empty extra_options don't appear in config."""
        conn = SSHConnection(
            name="no-extra",
            host="example.com",
            user="testuser",
            extra_options={},
        )

        config_block = conn.to_ssh_config_block()
        lines = config_block.split("\n")

        # Should only have the basic required lines
        expected_lines = [
            "Host no-extra",
            "    HostName example.com",
            "    User testuser",
            "",  # Final newline creates empty string
        ]

        assert lines == expected_lines

    def test_config_block_ends_with_newline(self):
        """Test that config block always ends with newline."""
        conn = SSHConnection(name="newline-test", host="example.com", user="testuser")

        config_block = conn.to_ssh_config_block()

        assert config_block.endswith("\n")

    def test_tags_field_functionality(self):
        """Test the tags field functionality."""
        conn = SSHConnection(
            name="tagged",
            host="example.com",
            user="testuser",
            tags=["production", "web", "critical"],
        )

        assert len(conn.tags) == 3
        assert "production" in conn.tags
        assert "web" in conn.tags
        assert "critical" in conn.tags

        # Tags should be preserved in serialization
        data = conn.model_dump()
        restored = SSHConnection(**data)
        assert restored.tags == conn.tags

    def test_pydantic_validation_errors(self):
        """Test that Pydantic validation works correctly."""
        # Test missing required fields
        with pytest.raises(ValueError):
            SSHConnection()  # Missing required fields

        with pytest.raises(ValueError):
            SSHConnection(name="test")  # Missing host and user

        with pytest.raises(ValueError):
            SSHConnection(name="test", host="example.com")  # Missing user

        # Test invalid port values
        with pytest.raises(ValueError):
            SSHConnection(name="test", host="example.com", user="test", port=0)

        with pytest.raises(ValueError):
            SSHConnection(name="test", host="example.com", user="test", port=65536)

    def test_model_config_dict(self):
        """Test that the model configuration is set correctly."""
        conn = SSHConnection(name="config-test", host="example.com", user="testuser")

        # The model_config should be present
        assert hasattr(SSHConnection, "model_config")
        assert SSHConnection.model_config is not None

    def test_field_descriptions(self):
        """Test that field descriptions are preserved."""
        # Get the model fields
        fields = SSHConnection.model_fields

        # Check that descriptions exist for key fields
        assert fields["name"].description == "Display name for the connection"
        assert fields["host"].description == "Hostname or IP address"
        assert fields["user"].description == "Username for SSH"
        assert fields["port"].description == "SSH port"
