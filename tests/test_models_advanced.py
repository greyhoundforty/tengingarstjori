"""Additional tests for SSH Connection models to improve coverage."""

from datetime import datetime

import pytest

# FIXED: Use correct import path for package structure
from tengingarstjori.models import SSHConnection


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
        # FIXED: Expect normalized format with space separator
        assert conn.local_forward == "8080 localhost:8080"
        assert conn.remote_forward == "9090 localhost:9090"
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
        """Test SSH config block includes non-standard ports."""
        conn = SSHConnection(
            name="custom-port-test",
            host="example.com",
            user="testuser",
            port=2222,
        )

        config_block = conn.to_ssh_config_block()

        assert "Host custom-port-test" in config_block
        assert "Port 2222" in config_block

    def test_ssh_config_block_with_standard_port(self):
        """Test SSH config block excludes standard port 22."""
        conn = SSHConnection(
            name="standard-port-test",
            host="example.com",
            user="testuser",
            port=22,
        )

        config_block = conn.to_ssh_config_block()

        assert "Host standard-port-test" in config_block
        assert "Port 22" not in config_block

    def test_ssh_config_block_with_all_advanced_options(self):
        """Test SSH config block with all advanced options."""
        conn = SSHConnection(
            name="advanced-test",
            host="example.com",
            user="testuser",
            identity_file="~/.ssh/special_key",
            proxy_jump="bastion.example.com",
            local_forward="3306:localhost:3306,8080:localhost:8080",
            remote_forward="9000:localhost:9000",
            extra_options={
                "StrictHostKeyChecking": "no",
                "ForwardAgent": "yes",
            },
            notes="Advanced configuration",
        )

        config_block = conn.to_ssh_config_block()

        assert "Host advanced-test" in config_block
        assert "# Advanced configuration" in config_block
        assert "IdentityFile ~/.ssh/special_key" in config_block
        assert "ProxyJump bastion.example.com" in config_block
        # FIXED: Expect normalized format with space separators
        assert "LocalForward 3306 localhost:3306" in config_block
        assert "LocalForward 8080 localhost:8080" in config_block
        assert "RemoteForward 9000 localhost:9000" in config_block
        assert "StrictHostKeyChecking no" in config_block
        assert "ForwardAgent yes" in config_block

    def test_ssh_config_block_notes_placement(self):
        """Test that notes are placed correctly in config block."""
        conn = SSHConnection(
            name="notes-test",
            host="example.com",
            user="testuser",
            notes="This is a test server",
        )

        config_block = conn.to_ssh_config_block()
        lines = config_block.strip().split("\n")

        assert lines[0] == "Host notes-test"
        assert lines[1] == "    # This is a test server"
        assert lines[2] == "    HostName example.com"

    def test_ssh_config_block_without_optional_fields(self):
        """Test SSH config block with only required fields."""
        conn = SSHConnection(
            name="minimal-test",
            host="example.com",
            user="testuser",
        )

        config_block = conn.to_ssh_config_block()

        assert "Host minimal-test" in config_block
        assert "HostName example.com" in config_block
        assert "User testuser" in config_block
        assert "Port" not in config_block  # Default port should not appear
        assert "IdentityFile" not in config_block
        assert "ProxyJump" not in config_block
        assert "LocalForward" not in config_block

    def test_update_usage_increments_correctly(self):
        """Test that usage statistics are updated correctly."""
        conn = SSHConnection(
            name="usage-test",
            host="example.com",
            user="testuser",
            use_count=5,
        )

        original_count = conn.use_count
        original_last_used = conn.last_used

        conn.update_usage()

        assert conn.use_count == original_count + 1
        assert conn.last_used != original_last_used
        assert isinstance(conn.last_used, datetime)

    def test_model_serialization_with_datetime(self):
        """Test model serialization handles datetime objects properly."""
        now = datetime.now()
        conn = SSHConnection(
            name="datetime-test",
            host="example.com",
            user="testuser",
            created_at=now,
            last_used=now,
        )

        # Test Python serialization (Pydantic V2 default behavior)
        # model_dump() returns Python objects by default
        data = conn.model_dump()
        assert isinstance(data["created_at"], datetime)

        # Test JSON serialization (when_used='json' applies here)
        # This is what gets used for JSON output
        json_str = conn.model_dump_json()
        assert now.isoformat() in json_str

        # Also test with mode='json'
        json_data = conn.model_dump(mode="json")
        assert isinstance(json_data["created_at"], str)
        assert json_data["created_at"] == now.isoformat()

        # Test that we can recreate from the data
        new_conn = SSHConnection(**data)
        assert new_conn.created_at == conn.created_at
        assert new_conn.last_used == conn.last_used

    def test_default_field_values(self):
        """Test that default field values are set correctly."""
        conn = SSHConnection(
            name="defaults-test",
            host="example.com",
            user="testuser",
        )

        assert conn.port == 22
        assert conn.use_count == 0
        assert conn.extra_options == {}
        assert conn.tags == []
        assert conn.last_used is None
        assert isinstance(conn.created_at, datetime)
        assert isinstance(conn.id, str)

    def test_extra_options_in_config_block(self):
        """Test that extra options are properly included in config block."""
        conn = SSHConnection(
            name="extra-test",
            host="example.com",
            user="testuser",
            extra_options={
                "ServerAliveInterval": "60",
                "ServerAliveCountMax": "3",
                "ControlMaster": "auto",
            },
        )

        config_block = conn.to_ssh_config_block()

        assert "ServerAliveInterval 60" in config_block
        assert "ServerAliveCountMax 3" in config_block
        assert "ControlMaster auto" in config_block

    def test_empty_extra_options(self):
        """Test behavior with empty extra_options dict."""
        conn = SSHConnection(
            name="empty-extra-test",
            host="example.com",
            user="testuser",
            extra_options={},
        )

        config_block = conn.to_ssh_config_block()

        # Should not contain any extra option lines
        lines = config_block.split("\n")
        option_lines = [
            line
            for line in lines
            if line.strip()
            and not line.startswith("Host")
            and not line.startswith("    HostName")
            and not line.startswith("    User")
        ]
        assert len(option_lines) == 0

    def test_config_block_ends_with_newline(self):
        """Test that config block always ends with a newline."""
        conn = SSHConnection(
            name="newline-test",
            host="example.com",
            user="testuser",
        )

        config_block = conn.to_ssh_config_block()
        assert config_block.endswith("\n")

    def test_tags_field_functionality(self):
        """Test tags field functionality."""
        conn = SSHConnection(
            name="tags-test",
            host="example.com",
            user="testuser",
            tags=["web", "production", "load-balancer"],
        )

        assert len(conn.tags) == 3
        assert "web" in conn.tags
        assert "production" in conn.tags
        assert "load-balancer" in conn.tags

        # Tags should not appear in SSH config block
        config_block = conn.to_ssh_config_block()
        assert "web" not in config_block
        assert "production" not in config_block

    def test_pydantic_validation_errors(self):
        """Test that Pydantic validation works correctly."""
        # Test missing required fields
        with pytest.raises(ValueError, match="Field required"):
            SSHConnection()  # Missing required fields

        with pytest.raises(ValueError, match="Field required"):
            SSHConnection(name="test")  # Missing host and user

        with pytest.raises(ValueError, match="Field required"):
            SSHConnection(name="test", host="example.com")  # Missing user

        # FIXED: Test invalid LocalForward format (this should raise ValueError)
        with pytest.raises(ValueError, match="Invalid LocalForward format"):
            SSHConnection(
                name="test",
                host="example.com",
                user="testuser",
                local_forward="invalid_format_no_colons",
            )

        # Test invalid RemoteForward format
        with pytest.raises(ValueError, match="Invalid RemoteForward format"):
            SSHConnection(
                name="test",
                host="example.com",
                user="testuser",
                remote_forward="3306::",  # Empty remote host
            )

        # Test invalid port numbers in forwards
        with pytest.raises(ValueError, match="must be numeric"):
            SSHConnection(
                name="test",
                host="example.com",
                user="testuser",
                local_forward="abc:localhost:3306",  # Non-numeric port
            )

    def test_model_config_dict(self):
        """Test that model configuration is set correctly."""
        # Test that the model has the expected configuration
        assert SSHConnection.model_config is not None

        # Pydantic V2: json_encoders is deprecated, using field_serializer instead
        # Verify datetime serialization works correctly
        conn = SSHConnection(name="config-test", host="example.com", user="testuser")

        # Verify that datetime fields exist and are datetime objects
        assert isinstance(conn.created_at, datetime)

        # Verify that datetime fields are serialized to ISO strings in JSON mode
        json_data = conn.model_dump(mode="json")
        assert isinstance(json_data["created_at"], str)
        assert json_data["created_at"] == conn.created_at.isoformat()

        # Verify Python mode returns datetime objects
        python_data = conn.model_dump()
        assert isinstance(python_data["created_at"], datetime)

    def test_field_descriptions(self):
        """Test that field descriptions are properly set."""
        # Get the model fields
        fields = SSHConnection.model_fields

        # Check that key fields have descriptions
        assert "Display name for the connection" in str(fields["name"])
        assert "Hostname or IP address" in str(fields["host"])
        assert "Username for SSH" in str(fields["user"])
        assert "SSH port" in str(fields["port"])

        # Test that optional fields have descriptions
        assert "Path to SSH private key" in str(fields["identity_file"])
        assert "ProxyJump configuration" in str(fields["proxy_jump"])
        assert "LocalForward configuration" in str(fields["local_forward"])
