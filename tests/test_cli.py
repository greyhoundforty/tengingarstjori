"""CLI Integration Tests for Tengingarstjóri."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from tengingarstjori.cli import add, cli, config, list, refresh, remove, show
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
    """Create a mock config manager with temporary directory."""
    with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
        manager = SSHConfigManager(config_dir=temp_config_dir)
        manager.mark_initialized()  # Mark as initialized
        mock_cm.return_value = manager
        yield manager


class TestCLICommands:
    """Test CLI command functionality."""

    def test_add_command_with_args(self, runner, mock_config_manager):
        """Test adding connection with CLI arguments."""
        result = runner.invoke(
            add,
            [
                "--name",
                "test-server",
                "--host",
                "192.168.1.100",
                "--user",
                "testuser",
                "--port",
                "2222",
                "--non-interactive",
            ],
        )

        assert result.exit_code == 0
        assert "Added connection 'test-server'" in result.output

        # Verify connection was added
        connections = mock_config_manager.list_connections()
        assert len(connections) == 1
        assert connections[0].name == "test-server"
        assert connections[0].host == "192.168.1.100"
        assert connections[0].user == "testuser"
        assert connections[0].port == 2222

    def test_add_command_missing_required_args(self, runner, mock_config_manager):
        """Test adding connection with missing required arguments."""
        result = runner.invoke(
            add, ["--name", "incomplete-server", "--non-interactive"]
        )

        # Should succeed but show error message
        assert "Host is required" in result.output

    def test_add_command_duplicate_name(self, runner, mock_config_manager):
        """Test adding connection with duplicate name."""
        # Add first connection
        conn = SSHConnection(name="duplicate", host="host1", user="user1")
        mock_config_manager.add_connection(conn)

        # Try to add duplicate
        result = runner.invoke(
            add,
            [
                "--name",
                "duplicate",
                "--host",
                "host2",
                "--user",
                "user2",
                "--non-interactive",
            ],
        )

        assert "already exists" in result.output

    def test_list_command_empty(self, runner, mock_config_manager):
        """Test listing connections when none exist."""
        result = runner.invoke(list, [])

        assert result.exit_code == 0
        assert "No connections configured" in result.output

    def test_list_command_with_connections(self, runner, mock_config_manager):
        """Test listing connections when they exist."""
        # Add test connections
        conn1 = SSHConnection(name="server1", host="host1", user="user1")
        conn2 = SSHConnection(name="server2", host="host2", user="user2", port=2222)
        mock_config_manager.add_connection(conn1)
        mock_config_manager.add_connection(conn2)

        result = runner.invoke(list, [])

        assert result.exit_code == 0
        assert "server1" in result.output
        assert "server2" in result.output
        assert "host1" in result.output
        assert "host2" in result.output
        assert "2222" in result.output

    def test_show_command_by_name(self, runner, mock_config_manager):
        """Test showing connection details by name."""
        conn = SSHConnection(
            name="show-test",
            host="example.com",
            user="testuser",
            port=2222,
            notes="Test connection",
        )
        mock_config_manager.add_connection(conn)

        result = runner.invoke(show, ["show-test"])

        assert result.exit_code == 0
        assert "show-test" in result.output
        assert "example.com" in result.output
        assert "testuser" in result.output
        assert "2222" in result.output
        assert "Test connection" in result.output

    def test_show_command_not_found(self, runner, mock_config_manager):
        """Test showing non-existent connection."""
        result = runner.invoke(show, ["nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.output

    def test_remove_command_by_name(self, runner, mock_config_manager):
        """Test removing connection by name."""
        conn = SSHConnection(name="remove-test", host="remove.com", user="removeuser")
        mock_config_manager.add_connection(conn)

        with patch("rich.prompt.Confirm.ask") as mock_confirm:
            mock_confirm.return_value = True  # Confirm deletion

            result = runner.invoke(remove, ["remove-test"])

            assert result.exit_code == 0
            assert "Removed connection 'remove-test'" in result.output

            # Verify connection was removed
            connections = mock_config_manager.list_connections()
            assert len(connections) == 0


class TestCLIArguments:
    """Test CLI argument parsing and validation."""

    def test_add_help(self, runner):
        """Test add command help."""
        result = runner.invoke(add, ["--help"])

        assert result.exit_code == 0
        assert "--name" in result.output
        assert "--host" in result.output
        assert "--user" in result.output
        assert "--port" in result.output

    def test_version_option(self, runner):
        """Test version option."""
        result = runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_main_help(self, runner):
        """Test main CLI help."""
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Tengingarstjóri" in result.output


class TestNonInteractiveMode:
    """Test CLI in non-interactive mode."""

    @pytest.mark.parametrize(
        "missing_arg,expected_error",
        [
            (["--host", "test.com", "--user", "test"], "Connection name is required"),
            (["--name", "test", "--user", "test"], "Host is required"),
            (["--name", "test", "--host", "test.com"], "Username is required"),
        ],
    )
    def test_non_interactive_missing_args(
        self, runner, mock_config_manager, missing_arg, expected_error
    ):
        """Test non-interactive mode with missing required arguments."""
        args = missing_arg + ["--non-interactive"]
        result = runner.invoke(add, args)

        # Should not fail, but should show error message
        assert expected_error in result.output

    def test_non_interactive_complete_args(self, runner, mock_config_manager):
        """Test non-interactive mode with all required arguments."""
        result = runner.invoke(
            add,
            [
                "--name",
                "complete",
                "--host",
                "complete.com",
                "--user",
                "completeuser",
                "--port",
                "22",
                "--key",
                "~/.ssh/id_rsa",
                "--notes",
                "Complete test",
                "--non-interactive",
            ],
        )

        assert result.exit_code == 0
        assert "Added connection 'complete'" in result.output

        # Verify all fields were set
        connections = mock_config_manager.list_connections()
        assert len(connections) == 1
        conn = connections[0]
        assert conn.name == "complete"
        assert conn.host == "complete.com"
        assert conn.user == "completeuser"
        assert conn.identity_file == "~/.ssh/id_rsa"
        assert conn.notes == "Complete test"


class TestErrorHandling:
    """Test error handling in CLI commands."""

    def test_uninitialized_config(self, runner):
        """Test commands when config manager is not initialized."""
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            manager = MagicMock()
            manager.is_initialized.return_value = False
            mock_cm.return_value = manager

            result = runner.invoke(
                add,
                [
                    "--name",
                    "test",
                    "--host",
                    "test.com",
                    "--user",
                    "test",
                    "--non-interactive",
                ],
            )

            assert result.exit_code == 0
            # FIXED: Account for Rich formatting - check for key phrases
            # Rich may wrap the text in ANSI codes or panels, so check for the core message
            output_text = result.output.lower()
            assert (
                "please run" in output_text
                and "tg init" in output_text
                and "first" in output_text
            )
