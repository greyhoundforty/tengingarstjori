"""Integration tests for the tengingarstjori package."""

import json
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from tengingarstjori.cli import cli
from tengingarstjori.config_manager import SSHConfigManager
from tengingarstjori.models import SSHConnection


@pytest.fixture
def temp_home_dir():
    """Create a temporary home directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def isolated_cli_runner(temp_home_dir, monkeypatch):
    """Create an isolated CLI runner with temporary home directory."""
    # Mock the home directory
    monkeypatch.setattr(Path, "home", lambda: temp_home_dir)

    runner = CliRunner()
    return runner


def test_cli_init_command(isolated_cli_runner):
    """Test the CLI init command."""
    result = isolated_cli_runner.invoke(cli, ["init"], input="y\n")

    assert result.exit_code == 0
    assert "Setup Complete" in result.output


def test_cli_add_command_non_interactive(isolated_cli_runner):
    """Test the CLI add command in non-interactive mode."""
    # First initialize
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")

    # Add a connection
    result = isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "test-server",
            "--host",
            "example.com",
            "--user",
            "testuser",
            "--port",
            "2222",
            "--non-interactive",
        ],
    )

    assert result.exit_code == 0
    assert "Added connection 'test-server'" in result.output


def test_cli_list_command(isolated_cli_runner):
    """Test the CLI list command."""
    # First initialize and add a connection
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")
    isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "test-server",
            "--host",
            "example.com",
            "--user",
            "testuser",
            "--non-interactive",
        ],
    )

    # List connections
    result = isolated_cli_runner.invoke(cli, ["list"])

    assert result.exit_code == 0
    assert "test-server" in result.output
    assert "example.com" in result.output
    assert "testuser" in result.output


def test_cli_list_detailed_command(isolated_cli_runner):
    """Test the CLI list command with detailed output."""
    # First initialize and add a connection with advanced options
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")
    isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "advanced-server",
            "--host",
            "example.com",
            "--user",
            "testuser",
            "--proxy-jump",
            "bastion.example.com",
            "--local-forward",
            "3306:localhost:3306",
            "--notes",
            "Test server with advanced options",
            "--non-interactive",
        ],
    )

    # List connections with detailed output
    result = isolated_cli_runner.invoke(cli, ["list", "--detailed"])

    assert result.exit_code == 0
    assert "advanced-server" in result.output
    assert "bastion.example.com" in result.output
    assert "3306:localhost:3306" in result.output
    assert "Test server with advanced options" in result.output


def test_cli_list_json_format(isolated_cli_runner):
    """Test the CLI list command with JSON output."""
    # First initialize and add a connection
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")
    isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "json-test-server",
            "--host",
            "example.com",
            "--user",
            "testuser",
            "--non-interactive",
        ],
    )

    # List connections in JSON format
    result = isolated_cli_runner.invoke(cli, ["list", "--format", "json"])

    assert result.exit_code == 0

    # Parse the JSON output
    json_output = json.loads(result.output)
    assert "connections" in json_output
    assert len(json_output["connections"]) == 1
    assert json_output["connections"][0]["name"] == "json-test-server"


def test_cli_show_command(isolated_cli_runner):
    """Test the CLI show command."""
    # First initialize and add a connection
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")
    isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "show-test-server",
            "--host",
            "example.com",
            "--user",
            "testuser",
            "--notes",
            "Test server for show command",
            "--non-interactive",
        ],
    )

    # Show connection details
    result = isolated_cli_runner.invoke(cli, ["show", "show-test-server"])

    assert result.exit_code == 0
    assert "show-test-server" in result.output
    assert "example.com" in result.output
    assert "testuser" in result.output
    assert "Test server for show command" in result.output
    assert "SSH Config Block" in result.output


def test_cli_remove_command(isolated_cli_runner):
    """Test the CLI remove command."""
    # First initialize and add a connection
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")
    isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "remove-test-server",
            "--host",
            "example.com",
            "--user",
            "testuser",
            "--non-interactive",
        ],
    )

    # Remove the connection
    result = isolated_cli_runner.invoke(
        cli, ["remove", "remove-test-server"], input="y\n"
    )

    assert result.exit_code == 0
    assert "Removed connection 'remove-test-server'" in result.output

    # Verify it's gone
    list_result = isolated_cli_runner.invoke(cli, ["list"])
    assert "remove-test-server" not in list_result.output


def test_cli_config_command(isolated_cli_runner):
    """Test the CLI config command."""
    # First initialize
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")

    # Run config command
    result = isolated_cli_runner.invoke(cli, ["config"], input="n\n")

    assert result.exit_code == 0
    assert "Configuration" in result.output
    assert "Current Settings" in result.output


def test_package_import():
    """Test that the package can be imported correctly."""
    # Imports are already at the top of the file
    # Test that main classes are available
    assert SSHConnection is not None
    assert SSHConfigManager is not None
    assert cli is not None

    # Test that we can create instances
    conn = SSHConnection(name="test", host="example.com", user="user")
    assert conn.name == "test"


def test_package_version():
    """Test that package version is accessible."""
    from tengingarstjori import __version__

    assert __version__ == "0.1.0"


def test_end_to_end_workflow(isolated_cli_runner):
    """Test a complete end-to-end workflow."""
    # 1. Initialize
    init_result = isolated_cli_runner.invoke(cli, ["init"], input="y\n")
    assert init_result.exit_code == 0

    # 2. Add multiple connections
    isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "web-server",
            "--host",
            "web.example.com",
            "--user",
            "webuser",
            "--port",
            "80",
            "--non-interactive",
        ],
    )

    isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "db-server",
            "--host",
            "db.example.com",
            "--user",
            "dbuser",
            "--proxy-jump",
            "bastion.example.com",
            "--local-forward",
            "3306:localhost:3306",
            "--notes",
            "Database server behind bastion",
            "--non-interactive",
        ],
    )

    # 3. List connections
    list_result = isolated_cli_runner.invoke(cli, ["list"])
    assert "web-server" in list_result.output
    assert "db-server" in list_result.output

    # 4. Show detailed info
    show_result = isolated_cli_runner.invoke(cli, ["show", "db-server"])
    assert "bastion.example.com" in show_result.output
    assert "3306:localhost:3306" in show_result.output

    # 5. Remove one connection
    isolated_cli_runner.invoke(cli, ["remove", "web-server"], input="y\n")

    # 6. Verify removal
    final_list = isolated_cli_runner.invoke(cli, ["list"])
    assert "web-server" not in final_list.output
    assert "db-server" in final_list.output


def test_error_handling_duplicate_connection(isolated_cli_runner):
    """Test error handling when adding duplicate connections."""
    # Initialize
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")

    # Add first connection
    result1 = isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "duplicate-test",
            "--host",
            "example.com",
            "--user",
            "user1",
            "--non-interactive",
        ],
    )
    assert result1.exit_code == 0

    # Try to add duplicate
    result2 = isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "duplicate-test",
            "--host",
            "different.com",
            "--user",
            "user2",
            "--non-interactive",
        ],
    )
    assert result2.exit_code == 0
    assert "already exists" in result2.output


def test_error_handling_missing_connection(isolated_cli_runner):
    """Test error handling when trying to access non-existent connection."""
    # Initialize
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")

    # Try to show non-existent connection
    result = isolated_cli_runner.invoke(cli, ["show", "non-existent"])
    assert result.exit_code == 0
    assert "not found" in result.output


def test_cli_refresh_command(isolated_cli_runner):
    """Test the CLI refresh command."""
    # Initialize and add a connection
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")
    isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "refresh-test",
            "--host",
            "example.com",
            "--user",
            "testuser",
            "--non-interactive",
        ],
    )

    # Run refresh command
    result = isolated_cli_runner.invoke(cli, ["refresh"])

    assert result.exit_code == 0
    assert "SSH configuration refreshed" in result.output


def test_complex_connection_with_all_options(isolated_cli_runner):
    """Test creating a connection with all possible options."""
    # Initialize
    isolated_cli_runner.invoke(cli, ["init"], input="y\n")

    # Add connection with all options
    result = isolated_cli_runner.invoke(
        cli,
        [
            "add",
            "--name",
            "complex-server",
            "--host",
            "complex.example.com",
            "--hostname",
            "10.0.1.100",
            "--user",
            "complexuser",
            "--port",
            "2222",
            "--key",
            "~/.ssh/complex_key",
            "--proxy-jump",
            "bastion.example.com",
            "--local-forward",
            "3306:localhost:3306,8080:localhost:8080",
            "--remote-forward",
            "9000:localhost:9000",
            "--notes",
            "Complex server with all options configured",
            "--non-interactive",
        ],
    )

    assert result.exit_code == 0
    assert "Added connection 'complex-server'" in result.output

    # Show the complex connection
    show_result = isolated_cli_runner.invoke(cli, ["show", "complex-server"])
    assert "complex-server" in show_result.output
    assert "10.0.1.100" in show_result.output
    assert "complexuser" in show_result.output
    assert "2222" in show_result.output
    assert "complex_key" in show_result.output
    assert "bastion.example.com" in show_result.output
    assert "3306:localhost:3306" in show_result.output
    assert "9000:localhost:9000" in show_result.output
    assert "Complex server with all options" in show_result.output
