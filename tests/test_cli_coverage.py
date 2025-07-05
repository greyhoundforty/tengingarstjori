"""Additional CLI tests to improve coverage."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from tengingarstjori.cli import cli, config, fix_config, init, refresh
from tengingarstjori.config_manager import SSHConfigManager
from tengingarstjori.models import SSHConnection


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config_manager(temp_config_dir):
    """Create a mock config manager."""
    with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
        manager = SSHConfigManager(config_dir=temp_config_dir)
        manager.mark_initialized()
        mock_cm.return_value = manager
        yield manager


class TestCLICommandsCoverage:
    """Additional CLI tests for better coverage."""

    def test_init_command_already_initialized(self, runner):
        """Test init command when already initialized."""
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            manager = MagicMock()
            manager.is_initialized.return_value = True
            mock_cm.return_value = manager

            result = runner.invoke(init)

            assert result.exit_code == 0
            assert "Already initialized" in result.output

    def test_init_command_new_setup(self, runner):
        """Test init command for new setup."""
        with (
            patch("tengingarstjori.cli.SSHConfigManager") as mock_cm,
            patch("tengingarstjori.cli.run_initial_setup") as mock_setup,
        ):
            manager = MagicMock()
            manager.is_initialized.return_value = False
            mock_cm.return_value = manager

            result = runner.invoke(init)

            assert result.exit_code == 0
            mock_setup.assert_called_once_with(manager)

    def test_config_command_no_update(self, runner, mock_config_manager):
        """Test config command without updating key."""
        mock_config_manager.get_setting = MagicMock(return_value="~/.ssh/id_rsa")

        with patch("tengingarstjori.cli.Confirm.ask", return_value=False):
            result = runner.invoke(config)

            assert result.exit_code == 0
            assert "Configuration" in result.output

    def test_config_command_update_with_available_keys(self, runner):
        """Test config command updating key with available keys."""
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            manager = MagicMock()
            manager.get_setting.return_value = "~/.ssh/id_rsa"
            manager.discover_ssh_keys.return_value = [
                "~/.ssh/id_rsa",
                "~/.ssh/id_ed25519",
            ]
            manager.update_setting = MagicMock()  # Ensure it's a Mock
            mock_cm.return_value = manager

            with (
                patch("tengingarstjori.cli.Confirm.ask", return_value=True),
                patch("tengingarstjori.cli.Prompt.ask", return_value="2"),
            ):
                result = runner.invoke(config)

                assert result.exit_code == 0
                manager.update_setting.assert_called()

    def test_config_command_update_with_custom_path(self, runner):
        """Test config command updating key with custom path."""
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            manager = MagicMock()
            manager.get_setting.return_value = "~/.ssh/id_rsa"
            manager.discover_ssh_keys.return_value = ["~/.ssh/id_rsa"]
            manager.update_setting = MagicMock()  # Ensure it's a Mock
            mock_cm.return_value = manager

            with (
                patch("tengingarstjori.cli.Confirm.ask", return_value=True),
                patch(
                    "tengingarstjori.cli.Prompt.ask", return_value="/custom/key/path"
                ),
            ):
                result = runner.invoke(config)

                assert result.exit_code == 0
                manager.update_setting.assert_called_with(
                    "default_identity_file", "/custom/key/path"
                )

    def test_config_command_no_available_keys(self, runner):
        """Test config command with no available keys."""
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            manager = MagicMock()
            manager.get_setting.return_value = "None"
            manager.discover_ssh_keys.return_value = []
            manager.update_setting = MagicMock()  # Ensure it's a Mock
            mock_cm.return_value = manager

            with (
                patch("tengingarstjori.cli.Confirm.ask", return_value=True),
                patch("tengingarstjori.cli.Prompt.ask", return_value="/new/key/path"),
            ):
                result = runner.invoke(config)

                assert result.exit_code == 0
                manager.update_setting.assert_called()

    def test_fix_config_command_with_existing_config(self, runner):
        """Test fix_config command with existing SSH config."""
        with (
            patch("tengingarstjori.cli.SSHConfigManager") as mock_cm,
            patch("pathlib.Path.home") as mock_home,
            patch("builtins.open") as mock_open,
            patch("pathlib.Path.exists", return_value=True),
        ):
            # Setup mocks
            manager = MagicMock()
            mock_cm.return_value = manager

            mock_home.return_value = Path("/home/user")
            mock_open.return_value.__enter__.return_value.read.return_value = (
                "Host test\n"
            )

            result = runner.invoke(fix_config)

            assert result.exit_code == 0
            assert "Fixing SSH configuration" in result.output

    def test_fix_config_command_error_handling(self, runner):
        """Test fix_config command error handling."""
        with (
            patch("tengingarstjori.cli.SSHConfigManager") as mock_cm,
            patch("pathlib.Path.home", side_effect=Exception("Test error")),
        ):
            manager = MagicMock()
            mock_cm.return_value = manager

            result = runner.invoke(fix_config)

            assert result.exit_code == 0
            assert "Error fixing SSH config" in result.output

    def test_refresh_command_success(self, runner):
        """Test refresh command success."""
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            manager = MagicMock()
            mock_cm.return_value = manager

            result = runner.invoke(refresh)

            assert result.exit_code == 0
            assert "Regenerating SSH configuration" in result.output
            manager._update_ssh_config.assert_called_once()

    def test_refresh_command_error(self, runner):
        """Test refresh command error handling."""
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            manager = MagicMock()
            manager._update_ssh_config.side_effect = Exception("Update failed")
            mock_cm.return_value = manager

            result = runner.invoke(refresh)

            assert result.exit_code == 0
            assert "Error refreshing config" in result.output

    def test_add_command_interactive_with_advanced_options(
        self, runner, mock_config_manager
    ):
        """Test add command interactive mode with advanced options."""
        mock_config_manager.discover_ssh_keys = MagicMock(return_value=[])
        mock_config_manager.get_setting = MagicMock(return_value=None)

        with (
            patch("tengingarstjori.cli.Prompt.ask") as mock_prompt,
            patch("tengingarstjori.cli.Confirm.ask") as mock_confirm,
        ):
            # Setup prompt responses for interactive mode
            mock_prompt.side_effect = [
                "test-server",  # name
                "example.com",  # host
                "testuser",  # user
                "22",  # port
                "",  # hostname (empty)
                "",  # key (empty)
                "bastion.com",  # proxy_jump
                "8080:localhost:8080",  # local_forward
                "",  # remote_forward (empty)
                "Test notes",  # notes
            ]

            # First confirm is for advanced options (True), second is implicit from flow
            mock_confirm.return_value = True

            result = runner.invoke(cli, ["add"])

            assert result.exit_code == 0

    def test_add_command_with_key_selection(self, runner, mock_config_manager):
        """Test add command with SSH key selection."""
        available_keys = ["~/.ssh/id_rsa", "~/.ssh/id_ed25519"]
        mock_config_manager.discover_ssh_keys = MagicMock(return_value=available_keys)
        mock_config_manager.get_setting = MagicMock(return_value="~/.ssh/id_rsa")

        with (
            patch("tengingarstjori.cli.Prompt.ask") as mock_prompt,
            patch("tengingarstjori.cli.Confirm.ask", return_value=False),
        ):
            mock_prompt.side_effect = [
                "key-test",  # name
                "example.com",  # host
                "testuser",  # user
                "22",  # port
                "",  # hostname (empty)
                "1",  # key selection (first key)
                "",  # notes (empty)
            ]

            result = runner.invoke(cli, ["add"])

            assert result.exit_code == 0

    def test_add_command_with_default_key(self, runner, mock_config_manager):
        """Test add command using default key."""
        available_keys = ["~/.ssh/id_rsa"]
        mock_config_manager.discover_ssh_keys = MagicMock(return_value=available_keys)
        mock_config_manager.get_setting = MagicMock(return_value="~/.ssh/id_rsa")

        with (
            patch("tengingarstjori.cli.Prompt.ask") as mock_prompt,
            patch("tengingarstjori.cli.Confirm.ask", return_value=False),
        ):
            mock_prompt.side_effect = [
                "default-test",  # name
                "example.com",  # host
                "testuser",  # user
                "22",  # port
                "",  # hostname (empty)
                "default",  # key selection (default)
                "",  # notes (empty)
            ]

            result = runner.invoke(cli, ["add"])

            assert result.exit_code == 0

    def test_add_command_connection_creation_failure(self, runner, mock_config_manager):
        """Test add command when connection creation fails."""
        mock_config_manager.add_connection = MagicMock(return_value=False)

        result = runner.invoke(
            cli,
            [
                "add",
                "--name",
                "fail-test",
                "--host",
                "example.com",
                "--user",
                "testuser",
                "--non-interactive",
            ],
        )

        assert result.exit_code == 0
        assert "Failed to add connection" in result.output

    def test_show_command_with_number_invalid_range(self, runner, mock_config_manager):
        """Test show command with number out of range."""
        # Add one connection
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        mock_config_manager.add_connection(conn)

        result = runner.invoke(cli, ["show", "999"])

        assert result.exit_code == 0
        assert "Invalid connection number" in result.output

    def test_remove_command_not_found(self, runner, mock_config_manager):
        """Test remove command with non-existent connection."""
        result = runner.invoke(cli, ["remove", "nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output

    def test_remove_command_by_number(self, runner, mock_config_manager):
        """Test remove command by number."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        mock_config_manager.add_connection(conn)

        with patch("tengingarstjori.cli.Confirm.ask", return_value=True):
            result = runner.invoke(cli, ["remove", "1"])

            assert result.exit_code == 0

    def test_remove_command_failed_removal(self, runner, mock_config_manager):
        """Test remove command when removal fails."""
        conn = SSHConnection(name="test", host="example.com", user="testuser")
        mock_config_manager.add_connection(conn)
        mock_config_manager.remove_connection = MagicMock(return_value=False)

        with patch("tengingarstjori.cli.Confirm.ask", return_value=True):
            result = runner.invoke(cli, ["remove", "test"])

            assert result.exit_code == 0
            assert "Failed to remove" in result.output


class TestCLIHelperFunctions:
    """Test CLI helper functions."""

    def test_get_required_field_interactive(self, runner):
        """Test _get_required_field helper in interactive mode."""
        from tengingarstjori.cli import _get_required_field

        with patch("tengingarstjori.cli.Prompt.ask", return_value="test_value"):
            result = _get_required_field(
                "test_field", None, True, "[cyan]Test prompt[/cyan]", "Test error"
            )
            assert result == "test_value"

    def test_get_required_field_non_interactive_with_value(self, runner):
        """Test _get_required_field helper with existing value."""
        from tengingarstjori.cli import _get_required_field

        result = _get_required_field(
            "test_field",
            "existing_value",
            False,
            "[cyan]Test prompt[/cyan]",
            "Test error",
        )
        assert result == "existing_value"

    def test_get_required_field_non_interactive_missing(self, runner):
        """Test _get_required_field helper missing value in non-interactive."""
        from tengingarstjori.cli import _get_required_field

        result = _get_required_field(
            "test_field", None, False, "[cyan]Test prompt[/cyan]", "Test error"
        )
        assert result is None

    def test_handle_ssh_key_selection_with_key(self, runner):
        """Test _handle_ssh_key_selection with existing key."""
        from tengingarstjori.cli import _handle_ssh_key_selection

        mock_manager = MagicMock()
        result = _handle_ssh_key_selection(mock_manager, "/existing/key", True)
        assert result == "/existing/key"

    def test_get_advanced_options_with_existing(self, runner):
        """Test _get_advanced_options with existing options."""
        from tengingarstjori.cli import _get_advanced_options

        proxy, local, remote = _get_advanced_options(
            True, "existing_proxy", "existing_local", "existing_remote"
        )
        assert proxy == "existing_proxy"
        assert local == "existing_local"
        assert remote == "existing_remote"

    def test_get_advanced_options_declined(self, runner):
        """Test _get_advanced_options when user declines."""
        from tengingarstjori.cli import _get_advanced_options

        with patch("tengingarstjori.cli.Confirm.ask", return_value=False):
            proxy, local, remote = _get_advanced_options(True, None, None, None)
            assert proxy is None
            assert local is None
            assert remote is None

    def test_find_connection_by_ref_helper(self, runner):
        """Test _find_connection_by_ref helper function."""
        from tengingarstjori.cli import _find_connection_by_ref

        mock_manager = MagicMock()
        mock_connection = MagicMock()
        mock_manager.list_connections.return_value = [mock_connection]

        # Test by number
        result = _find_connection_by_ref(mock_manager, "1")
        assert result == mock_connection

        # Test by name
        mock_manager.get_connection_by_name.return_value = mock_connection
        result = _find_connection_by_ref(mock_manager, "test-name")
        assert result == mock_connection
