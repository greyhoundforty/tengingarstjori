"""Tests for new CLI commands: connect, clone, test, history, snippet, export, import, list filters."""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from tengingarstjori.cli import (
    cli,
    clone,
    connect,
    export_cmd,
    history,
    import_cmd,
    list,
    snippet,
    test,
)
from tengingarstjori.config_manager import SSHConfigManager
from tengingarstjori.models import SSHConnection


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_config_dir():
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config_manager(temp_config_dir):
    with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
        manager = SSHConfigManager(config_dir=temp_config_dir)
        manager.mark_initialized()
        mock_cm.return_value = manager
        yield manager


@pytest.fixture
def sample_connections(mock_config_manager):
    now = datetime.now()
    conns = [
        SSHConnection(
            name="prod-web",
            host="10.0.1.10",
            user="admin",
            port=22,
            identity_file="~/.ssh/id_ed25519",
            tags=["production", "web"],
            notes="Production web server",
            last_used=now - timedelta(hours=1),
            use_count=15,
        ),
        SSHConnection(
            name="staging-db",
            host="10.0.2.20",
            user="dbadmin",
            port=5432,
            tags=["staging", "database"],
            notes="Staging database",
            last_used=now - timedelta(days=7),
            use_count=3,
        ),
        SSHConnection(
            name="bastion",
            host="bastion.example.com",
            user="jump",
            proxy_jump=None,
            tags=["production", "infra"],
            notes="Jump host",
            last_used=None,
            use_count=0,
        ),
    ]
    for conn in conns:
        mock_config_manager.add_connection(conn)
    return conns


class TestConnectCommand:
    def test_connect_dry_run(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(connect, ["prod-web", "--dry-run"])
        assert result.exit_code == 0
        assert "ssh prod-web" in result.output

    def test_connect_dry_run_by_number(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(connect, ["1", "--dry-run"])
        assert result.exit_code == 0
        assert "ssh prod-web" in result.output

    def test_connect_updates_usage(
        self, runner, mock_config_manager, sample_connections
    ):
        old_count = sample_connections[0].use_count
        result = runner.invoke(connect, ["prod-web", "--dry-run"])
        assert result.exit_code == 0
        conn = mock_config_manager.get_connection_by_name("prod-web")
        assert conn.use_count == old_count + 1
        assert conn.last_used is not None

    def test_connect_not_found(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(connect, ["nonexistent", "--dry-run"])
        assert "not found" in result.output

    def test_connect_not_initialized(self, runner):
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            mgr = MagicMock()
            mgr.is_initialized.return_value = False
            mock_cm.return_value = mgr
            result = runner.invoke(connect, ["test"])
            assert "tg init" in result.output

    def test_connect_execvp(self, runner, mock_config_manager, sample_connections):
        with patch("tengingarstjori.cli.os.execvp") as mock_exec:
            result = runner.invoke(connect, ["prod-web"])
            mock_exec.assert_called_once_with("ssh", ["ssh", "prod-web"])


class TestListFilters:
    def test_list_filter_by_tag(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(list, ["--tag", "production"])
        assert result.exit_code == 0
        assert "prod-web" in result.output
        assert "bastion" in result.output
        assert "staging-db" not in result.output

    def test_list_filter_by_search(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(list, ["--search", "bastion"])
        assert result.exit_code == 0
        assert "bastion" in result.output
        assert "prod-web" not in result.output

    def test_list_search_in_notes(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(list, ["--search", "database"])
        assert result.exit_code == 0
        assert "staging-db" in result.output

    def test_list_filter_unused(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(list, ["--unused"])
        assert result.exit_code == 0
        assert "bastion" in result.output
        assert "prod-web" not in result.output

    def test_list_sort_by_name(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(list, ["--sort", "name"])
        assert result.exit_code == 0
        lines = result.output.splitlines()
        name_lines = [
            line
            for line in lines
            if "bastion" in line or "prod-web" in line or "staging-db" in line
        ]
        assert len(name_lines) == 3

    def test_list_sort_by_use_count(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(list, ["--sort", "use-count", "-f", "json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data[0]["name"] == "prod-web"

    def test_list_combined_filters(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(list, ["--tag", "production", "--search", "web"])
        assert result.exit_code == 0
        assert "prod-web" in result.output
        assert "bastion" not in result.output

    def test_list_no_results(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(list, ["--tag", "nonexistent"])
        assert result.exit_code == 0
        assert "No connections" in result.output


class TestCloneCommand:
    def test_clone_basic(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(clone, ["prod-web", "prod-web-clone"])
        assert result.exit_code == 0
        assert "Cloned" in result.output
        cloned = mock_config_manager.get_connection_by_name("prod-web-clone")
        assert cloned is not None
        assert cloned.host == "10.0.1.10"
        assert cloned.user == "admin"
        assert cloned.use_count == 0
        assert cloned.last_used is None

    def test_clone_by_number(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(clone, ["1", "clone-of-first"])
        assert result.exit_code == 0
        assert "Cloned" in result.output

    def test_clone_duplicate_name(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(clone, ["prod-web", "staging-db"])
        assert "already exists" in result.output

    def test_clone_source_not_found(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(clone, ["nonexistent", "new-name"])
        assert "not found" in result.output

    def test_clone_not_initialized(self, runner):
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            mgr = MagicMock()
            mgr.is_initialized.return_value = False
            mock_cm.return_value = mgr
            result = runner.invoke(clone, ["a", "b"])
            assert "tg init" in result.output

    def test_clone_preserves_tags(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(clone, ["prod-web", "prod-web-v2"])
        assert result.exit_code == 0
        cloned = mock_config_manager.get_connection_by_name("prod-web-v2")
        assert "production" in cloned.tags
        assert "web" in cloned.tags


class TestTestCommand:
    def test_test_single_success(self, runner, mock_config_manager, sample_connections):
        with patch("tengingarstjori.cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr=b"")
            result = runner.invoke(test, ["prod-web"])
            assert result.exit_code == 0
            assert "OK" in result.output

    def test_test_single_failure(self, runner, mock_config_manager, sample_connections):
        with patch("tengingarstjori.cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=255, stderr=b"Connection refused"
            )
            result = runner.invoke(test, ["prod-web"])
            assert "Failed" in result.output

    def test_test_timeout(self, runner, mock_config_manager, sample_connections):
        with patch("tengingarstjori.cli.subprocess.run") as mock_run:
            mock_run.side_effect = __import__("subprocess").TimeoutExpired(
                cmd="ssh", timeout=5
            )
            result = runner.invoke(test, ["prod-web"])
            assert "Timeout" in result.output

    def test_test_all_connections(
        self, runner, mock_config_manager, sample_connections
    ):
        with patch("tengingarstjori.cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr=b"")
            result = runner.invoke(test, ["--all"])
            assert result.exit_code == 0
            assert "prod-web" in result.output
            assert "staging-db" in result.output
            assert "bastion" in result.output

    def test_test_no_args(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(test, [])
        assert "Provide a connection name" in result.output

    def test_test_custom_timeout(self, runner, mock_config_manager, sample_connections):
        with patch("tengingarstjori.cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stderr=b"")
            result = runner.invoke(test, ["prod-web", "-t", "10"])
            assert result.exit_code == 0
            call_args = mock_run.call_args[0][0]
            assert "ConnectTimeout=10" in " ".join(call_args)


class TestHistoryCommand:
    def test_history_basic(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(history)
        assert result.exit_code == 0
        assert "prod-web" in result.output
        assert "staging-db" in result.output
        assert "bastion" not in result.output

    def test_history_order(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(history, ["-f", "json"] if False else [])
        assert result.exit_code == 0
        lines = result.output.splitlines()
        prod_idx = next((i for i, l in enumerate(lines) if "prod-web" in l), None)
        staging_idx = next((i for i, l in enumerate(lines) if "staging-db" in l), None)
        assert prod_idx is not None
        assert staging_idx is not None
        assert prod_idx < staging_idx

    def test_history_limit(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(history, ["-n", "1"])
        assert result.exit_code == 0
        assert "prod-web" in result.output

    def test_history_empty(self, runner, mock_config_manager):
        result = runner.invoke(history)
        assert "No connection history" in result.output

    def test_history_show_all(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(history, ["--all"])
        assert result.exit_code == 0
        assert "prod-web" in result.output


class TestSnippetCommand:
    def test_snippet_basic_command(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(snippet, ["prod-web"])
        assert result.exit_code == 0
        assert "ssh" in result.output
        assert "admin@10.0.1.10" in result.output
        assert "-i ~/.ssh/id_ed25519" in result.output

    def test_snippet_custom_port(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(snippet, ["staging-db"])
        assert result.exit_code == 0
        assert "-p 5432" in result.output

    def test_snippet_config_block(
        self, runner, mock_config_manager, sample_connections
    ):
        result = runner.invoke(snippet, ["prod-web", "--config"])
        assert result.exit_code == 0
        assert "Host prod-web" in result.output
        assert "HostName 10.0.1.10" in result.output
        assert "User admin" in result.output

    def test_snippet_not_found(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(snippet, ["nonexistent"])
        assert "not found" in result.output


class TestExportCommand:
    def test_export_json_stdout(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(export_cmd)
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 3
        names = {c["name"] for c in data}
        assert "prod-web" in names

    def test_export_json_to_file(self, runner, mock_config_manager, sample_connections):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            result = runner.invoke(export_cmd, ["-o", path])
            assert result.exit_code == 0
            assert "Exported 3 connections" in result.output
            data = json.loads(Path(path).read_text())
            assert len(data) == 3
        finally:
            Path(path).unlink(missing_ok=True)

    def test_export_ssh_config(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(export_cmd, ["-f", "ssh-config"])
        assert result.exit_code == 0
        assert "Host prod-web" in result.output
        assert "Host staging-db" in result.output

    def test_export_strip_keys(self, runner, mock_config_manager, sample_connections):
        result = runner.invoke(export_cmd, ["--strip-keys"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        for conn in data:
            assert "identity_file" not in conn or conn["identity_file"] is None

    def test_export_empty(self, runner, mock_config_manager):
        result = runner.invoke(export_cmd)
        assert "No connections to export" in result.output


class TestImportCommand:
    def test_import_basic(self, runner, mock_config_manager):
        data = [
            {"name": "imported-1", "host": "10.0.0.1", "user": "root"},
            {"name": "imported-2", "host": "10.0.0.2", "user": "admin"},
        ]
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = runner.invoke(import_cmd, [path])
            assert result.exit_code == 0
            assert "Imported: 2" in result.output
            assert mock_config_manager.get_connection_by_name("imported-1") is not None
        finally:
            Path(path).unlink(missing_ok=True)

    def test_import_skip_existing(
        self, runner, mock_config_manager, sample_connections
    ):
        data = [{"name": "prod-web", "host": "10.0.0.99", "user": "other"}]
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = runner.invoke(import_cmd, [path])
            assert "Skipped" in result.output
            conn = mock_config_manager.get_connection_by_name("prod-web")
            assert conn.host == "10.0.1.10"  # unchanged
        finally:
            Path(path).unlink(missing_ok=True)

    def test_import_overwrite(self, runner, mock_config_manager, sample_connections):
        data = [{"name": "prod-web", "host": "10.0.0.99", "user": "newuser"}]
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = runner.invoke(import_cmd, [path, "--strategy", "overwrite"])
            assert "Imported: 1" in result.output
            conn = mock_config_manager.get_connection_by_name("prod-web")
            assert conn.host == "10.0.0.99"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_import_rename(self, runner, mock_config_manager, sample_connections):
        data = [{"name": "prod-web", "host": "10.0.0.99", "user": "other"}]
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = runner.invoke(import_cmd, [path, "--strategy", "rename"])
            assert "Imported: 1" in result.output
            renamed = mock_config_manager.get_connection_by_name("prod-web-2")
            assert renamed is not None
            assert renamed.host == "10.0.0.99"
        finally:
            Path(path).unlink(missing_ok=True)

    def test_import_file_not_found(self, runner, mock_config_manager):
        result = runner.invoke(import_cmd, ["/nonexistent/file.json"])
        assert "File not found" in result.output

    def test_import_invalid_json(self, runner, mock_config_manager):
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write("not json{{{")
            path = f.name
        try:
            result = runner.invoke(import_cmd, [path])
            assert "Invalid JSON" in result.output
        finally:
            Path(path).unlink(missing_ok=True)

    def test_import_not_array(self, runner, mock_config_manager):
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump({"name": "test"}, f)
            path = f.name
        try:
            result = runner.invoke(import_cmd, [path])
            assert "Expected a JSON array" in result.output
        finally:
            Path(path).unlink(missing_ok=True)

    def test_import_not_initialized(self, runner):
        with patch("tengingarstjori.cli.SSHConfigManager") as mock_cm:
            mgr = MagicMock()
            mgr.is_initialized.return_value = False
            mock_cm.return_value = mgr
            result = runner.invoke(import_cmd, ["/tmp/test.json"])
            assert "tg init" in result.output


class TestExportImportRoundTrip:
    def test_roundtrip(self, runner, mock_config_manager, sample_connections):
        export_result = runner.invoke(export_cmd)
        assert export_result.exit_code == 0
        data = json.loads(export_result.output)

        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump(data, f)
            path = f.name

        for conn in mock_config_manager.list_connections():
            mock_config_manager.remove_connection(conn.id)
        assert len(mock_config_manager.list_connections()) == 0

        try:
            import_result = runner.invoke(import_cmd, [path])
            assert import_result.exit_code == 0
            assert "Imported: 3" in import_result.output
            assert len(mock_config_manager.list_connections()) == 3
        finally:
            Path(path).unlink(missing_ok=True)
