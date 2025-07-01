"""Additional tests for SSH Config Manager to improve coverage."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.config_manager import SSHConfigManager
from src.models import SSHConnection


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def config_manager(temp_config_dir):
    """Create a config manager with temporary directory."""
    return SSHConfigManager(config_dir=temp_config_dir)


class TestSSHConfigManagerAdvanced:
    """Advanced tests for SSH Config Manager."""

    def test_load_data_with_corrupted_connections(self, temp_config_dir):
        """Test loading corrupted connections file."""
        connections_file = temp_config_dir / "connections.json"
        connections_file.write_text("{ invalid json")

        # Should handle gracefully
        manager = SSHConfigManager(config_dir=temp_config_dir)
        assert len(manager.connections) == 0

    def test_load_data_with_corrupted_settings(self, temp_config_dir):
        """Test loading corrupted settings file."""
        settings_file = temp_config_dir / "settings.json"
        settings_file.write_text("{ invalid json")

        # Should handle gracefully
        manager = SSHConfigManager(config_dir=temp_config_dir)
        assert len(manager.settings) == 0

    def test_save_connections_error_handling(self, config_manager):
        """Test error handling in save_connections."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        config_manager.connections.append(conn)

        # Mock file operations to raise exception
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            # Should handle gracefully without crashing
            config_manager._save_connections()

    def test_save_settings_error_handling(self, config_manager):
        """Test error handling in save_settings."""
        config_manager.settings["test"] = "value"

        # Mock file operations to raise exception
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            # Should handle gracefully without crashing
            config_manager._save_settings()

    def test_update_ssh_config_error_handling(self, config_manager):
        """Test error handling in update_ssh_config."""
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            # Should handle gracefully without crashing
            config_manager._update_ssh_config()

    def test_ensure_include_line_with_existing_config(self, config_manager):
        """Test ensure_include_line with existing SSH config."""
        with (
            patch("pathlib.Path.exists", return_value=True),
            patch(
                "builtins.open",
                mock_open(read_data="Host existing\n    HostName existing.com\n"),
            ) as mock_file,
            patch("shutil.copy2") as mock_copy,
        ):
            config_manager._ensure_include_line()

            # Should have attempted to read and write the config
            mock_file.assert_called()

    def test_ensure_include_line_with_existing_include(self, config_manager):
        """Test ensure_include_line when include already exists."""
        include_line = f"Include {config_manager.managed_config}"
        existing_content = f"{include_line}\nHost existing\n    HostName existing.com\n"

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=existing_content)),
        ):
            # Should not modify file if include already exists
            config_manager._ensure_include_line()

    def test_ensure_include_line_with_corrupted_lines(self, config_manager):
        """Test ensure_include_line with corrupted include lines."""
        corrupted_content = f"Include {config_manager.managed_config}\\n\\nHost test\n"

        with (
            patch("pathlib.Path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=corrupted_content)) as mock_file,
            patch("shutil.copy2") as mock_copy,
        ):
            config_manager._ensure_include_line()

            # Should have cleaned up corrupted lines
            mock_copy.assert_called()

    def test_discover_ssh_keys_with_custom_keys(self, config_manager):
        """Test discovering SSH keys including custom keys."""
        # Create mock files for SSH directory
        mock_key_file = MagicMock()
        mock_key_file.is_file.return_value = True
        mock_key_file.suffix = ""
        mock_key_file.name = "custom_key"

        mock_non_key_file = MagicMock()
        mock_non_key_file.is_file.return_value = True
        mock_non_key_file.suffix = ""
        mock_non_key_file.name = "not_a_key"

        with (
            # Mock standard key existence
            patch.object(
                config_manager.ssh_dir,
                "glob",
                return_value=[mock_key_file, mock_non_key_file],
            ),
            # Mock file reading
            patch(
                "builtins.open", mock_open(read_data="-----BEGIN PRIVATE KEY-----\n")
            ) as mock_file,
        ):
            # Mock path exists for standard keys
            def mock_exists(self):
                return str(self).endswith(("id_rsa", "id_ed25519"))

            with patch.object(Path, "exists", mock_exists):
                keys = config_manager.discover_ssh_keys()

            # Should find standard keys and the custom key
            assert len(keys) >= 2

    def test_discover_ssh_keys_read_error(self, config_manager):
        """Test SSH key discovery with file read errors."""
        mock_file = MagicMock()
        mock_file.is_file.return_value = True
        mock_file.suffix = ""
        mock_file.name = "unreadable_key"

        with (
            patch.object(config_manager.ssh_dir, "glob", return_value=[mock_file]),
            patch("builtins.open", side_effect=OSError("Permission denied")),
        ):
            # Should handle file read errors gracefully
            keys = config_manager.discover_ssh_keys()
            assert isinstance(keys, list)

    def test_add_connection_error_handling(self, config_manager):
        """Test add_connection error handling."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")

        # Mock _save_connections to raise an exception
        with patch.object(
            config_manager, "_save_connections", side_effect=Exception("Save failed")
        ):
            result = config_manager.add_connection(conn)
            assert result is False

    def test_remove_connection_error_handling(self, config_manager):
        """Test remove_connection error handling."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        config_manager.add_connection(conn)

        # Mock _save_connections to raise an exception
        with patch.object(
            config_manager, "_save_connections", side_effect=Exception("Save failed")
        ):
            result = config_manager.remove_connection(conn.id)
            assert result is False

    def test_remove_nonexistent_connection(self, config_manager):
        """Test removing a connection that doesn't exist."""
        result = config_manager.remove_connection("nonexistent-id")
        assert result is False

    def test_update_connection_error_handling(self, config_manager):
        """Test update_connection error handling."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        config_manager.add_connection(conn)

        # Modify the connection
        conn.host = "updated.com"

        # Mock _save_connections to raise an exception
        with patch.object(
            config_manager, "_save_connections", side_effect=Exception("Save failed")
        ):
            result = config_manager.update_connection(conn)
            assert result is False

    def test_update_nonexistent_connection(self, config_manager):
        """Test updating a connection that doesn't exist."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        result = config_manager.update_connection(conn)
        assert result is False

    def test_get_connection(self, config_manager):
        """Test get_connection method."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        config_manager.add_connection(conn)

        # Test finding existing connection
        found = config_manager.get_connection(conn.id)
        assert found is not None
        assert found.id == conn.id

        # Test finding non-existent connection
        not_found = config_manager.get_connection("nonexistent-id")
        assert not_found is None

    def test_list_connections_returns_copy(self, config_manager):
        """Test that list_connections returns a copy."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        config_manager.add_connection(conn)

        connections = config_manager.list_connections()

        # Modify the returned list
        connections.clear()

        # Original should be unchanged
        assert len(config_manager.connections) == 1

    def test_update_setting(self, config_manager):
        """Test update_setting method."""
        config_manager.update_setting("test_key", "test_value")
        assert config_manager.settings["test_key"] == "test_value"

    def test_get_setting_with_default(self, config_manager):
        """Test get_setting with default value."""
        # Test getting non-existent setting with default
        result = config_manager.get_setting("nonexistent", "default_value")
        assert result == "default_value"

        # Test getting existing setting
        config_manager.settings["existing"] = "existing_value"
        result = config_manager.get_setting("existing", "default_value")
        assert result == "existing_value"

    def test_is_initialized(self, config_manager):
        """Test is_initialized method."""
        # Initially should not be initialized
        assert not config_manager.is_initialized()

        # After marking as initialized
        config_manager.mark_initialized()
        assert config_manager.is_initialized()

    def test_mark_initialized(self, config_manager):
        """Test mark_initialized method."""
        config_manager.mark_initialized()

        assert config_manager.get_setting("initialized") is True
        assert config_manager.get_setting("initialized_at") is not None

    def test_ssh_config_generation_with_multiple_connections(self, config_manager):
        """Test SSH config generation with multiple connections."""
        conn1 = SSHConnection(name="server1", host="host1.com", user="user1")
        conn2 = SSHConnection(name="server2", host="host2.com", user="user2", port=2222)

        config_manager.add_connection(conn1)
        config_manager.add_connection(conn2)

        # Should be able to update config without errors
        config_manager._update_ssh_config()

    def test_ssh_directory_creation_with_permissions(self, temp_config_dir):
        """Test SSH directory creation with proper permissions."""
        with patch("pathlib.Path.home", return_value=temp_config_dir):
            manager = SSHConfigManager()

            ssh_dir = temp_config_dir / ".ssh"
            assert ssh_dir.exists()

            # Check permissions (should be 700)
            stat_result = ssh_dir.stat()
            permissions = oct(stat_result.st_mode)[-3:]
            assert permissions == "700"

    def test_config_directory_creation(self, tmp_path):
        """Test configuration directory creation."""
        config_dir = tmp_path / "custom_config"
        manager = SSHConfigManager(config_dir=config_dir)

        assert config_dir.exists()
        assert manager.config_dir == config_dir
