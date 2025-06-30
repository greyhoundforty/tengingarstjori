"""
CLI Integration Tests for Tengingarstjóri
"""

import pytest
import tempfile
import json
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from src.cli import cli, add, list, show, remove, config, refresh, fix_config
from src.config_manager import SSHConfigManager
from src.models import SSHConnection


@pytest.fixture
def runner():
    """Create a CLI test runner"""
    return CliRunner()


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_config_manager(temp_config_dir):
    """Create a mock config manager with temporary directory"""
    with patch('src.cli.SSHConfigManager') as mock_cm:
        manager = SSHConfigManager(config_dir=temp_config_dir)
        manager.mark_initialized()  # Mark as initialized
        mock_cm.return_value = manager
        yield manager


class TestCLICommands:
    """Test CLI command functionality"""
    
    def test_add_command_with_args(self, runner, mock_config_manager):
        """Test adding connection with CLI arguments"""
        result = runner.invoke(add, [
            '--name', 'test-server',
            '--host', '192.168.1.100',
            '--user', 'testuser',
            '--port', '2222',
            '--non-interactive'
        ])
        
        assert result.exit_code == 0
        assert "Added connection 'test-server'" in result.output
        
        # Verify connection was added
        connections = mock_config_manager.list_connections()
        assert len(connections) == 1
        assert connections[0].name == 'test-server'
        assert connections[0].host == '192.168.1.100'
        assert connections[0].user == 'testuser'
        assert connections[0].port == 2222
    
    def test_add_command_interactive_mode(self, runner, mock_config_manager):
        """Test adding connection in interactive mode"""
        # Mock the prompts
        with patch('src.cli.Prompt.ask') as mock_prompt, \
             patch('src.cli.Confirm.ask') as mock_confirm:
            
            # Setup prompt responses
            mock_prompt.side_effect = [
                'interactive-server',  # name
                '10.0.0.1',           # host
                'admin',              # user
                '22',                 # port
                '',                   # hostname (empty)
                'default',            # key choice
                '',                   # notes (empty)
            ]
            mock_confirm.return_value = False  # No advanced options
            
            # Mock available keys
            mock_config_manager.discover_ssh_keys = MagicMock(return_value=['/home/user/.ssh/id_rsa'])
            mock_config_manager.get_setting = MagicMock(return_value='/home/user/.ssh/id_rsa')
            
            result = runner.invoke(add, [])
            
            assert result.exit_code == 0
            assert "Added connection 'interactive-server'" in result.output
    
    def test_add_command_missing_required_args(self, runner, mock_config_manager):
        """Test adding connection with missing required arguments"""
        result = runner.invoke(add, [
            '--name', 'incomplete-server',
            '--no-interactive'
        ])
        
        assert result.exit_code == 0
        assert "Host is required" in result.output
    
    def test_add_command_duplicate_name(self, runner, mock_config_manager):
        """Test adding connection with duplicate name"""
        # Add first connection
        conn = SSHConnection(name='duplicate', host='host1', user='user1')
        mock_config_manager.add_connection(conn)
        
        # Try to add duplicate
        result = runner.invoke(add, [
            '--name', 'duplicate',
            '--host', 'host2',
            '--user', 'user2',
            '--no-interactive'
        ])
        
        assert result.exit_code == 0
        assert "already exists" in result.output
    
    def test_list_command_empty(self, runner, mock_config_manager):
        """Test listing connections when none exist"""
        result = runner.invoke(list, [])
        
        assert result.exit_code == 0
        assert "No connections configured" in result.output
    
    def test_list_command_with_connections(self, runner, mock_config_manager):
        """Test listing connections when they exist"""
        # Add test connections
        conn1 = SSHConnection(name='server1', host='host1', user='user1')
        conn2 = SSHConnection(name='server2', host='host2', user='user2', port=2222)
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
        """Test showing connection details by name"""
        conn = SSHConnection(
            name='show-test',
            host='example.com',
            user='testuser',
            port=2222,
            notes='Test connection'
        )
        mock_config_manager.add_connection(conn)
        
        result = runner.invoke(show, ['show-test'])
        
        assert result.exit_code == 0
        assert "show-test" in result.output
        assert "example.com" in result.output
        assert "testuser" in result.output
        assert "2222" in result.output
        assert "Test connection" in result.output
    
    def test_show_command_by_number(self, runner, mock_config_manager):
        """Test showing connection details by number"""
        conn = SSHConnection(name='numbered', host='numbered.com', user='numuser')
        mock_config_manager.add_connection(conn)
        
        result = runner.invoke(show, ['1'])
        
        assert result.exit_code == 0
        assert "numbered" in result.output
        assert "numbered.com" in result.output
    
    def test_show_command_not_found(self, runner, mock_config_manager):
        """Test showing non-existent connection"""
        result = runner.invoke(show, ['nonexistent'])
        
        assert result.exit_code == 0
        assert "not found" in result.output
    
    def test_remove_command_by_name(self, runner, mock_config_manager):
        """Test removing connection by name"""
        conn = SSHConnection(name='remove-test', host='remove.com', user='removeuser')
        mock_config_manager.add_connection(conn)
        
        with patch('src.cli.Confirm.ask') as mock_confirm:
            mock_confirm.return_value = True  # Confirm deletion
            
            result = runner.invoke(remove, ['remove-test'])
            
            assert result.exit_code == 0
            assert "Removed connection 'remove-test'" in result.output
            
            # Verify connection was removed
            connections = mock_config_manager.list_connections()
            assert len(connections) == 0
    
    def test_remove_command_cancelled(self, runner, mock_config_manager):
        """Test removing connection but cancel"""
        conn = SSHConnection(name='cancel-test', host='cancel.com', user='canceluser')
        mock_config_manager.add_connection(conn)
        
        with patch('src.cli.Confirm.ask') as mock_confirm:
            mock_confirm.return_value = False  # Cancel deletion
            
            result = runner.invoke(remove, ['cancel-test'])
            
            assert result.exit_code == 0
            assert "Cancelled" in result.output
            
            # Verify connection still exists
            connections = mock_config_manager.list_connections()
            assert len(connections) == 1


class TestCLIArguments:
    """Test CLI argument parsing and validation"""
    
    def test_add_help(self, runner):
        """Test add command help"""
        result = runner.invoke(add, ['--help'])
        
        assert result.exit_code == 0
        assert "--name" in result.output
        assert "--host" in result.output
        assert "--user" in result.output
        assert "--port" in result.output
        assert "Examples:" in result.output
    
    def test_version_option(self, runner):
        """Test version option"""
        result = runner.invoke(cli, ['--version'])
        
        assert result.exit_code == 0
        assert "0.1.0" in result.output
    
    def test_main_help(self, runner):
        """Test main CLI help"""
        result = runner.invoke(cli, ['--help'])
        
        assert result.exit_code == 0
        assert "Tengingarstjóri" in result.output
        assert "init" in result.output
        assert "add" in result.output
        assert "list" in result.output


class TestCLIValidation:
    """Test CLI input validation"""
    
    def test_add_invalid_port(self, runner, mock_config_manager):
        """Test adding connection with invalid port"""
        result = runner.invoke(add, [
            '--name', 'test-server',
            '--host', '192.168.1.100',
            '--user', 'testuser',
            '--port', 'invalid',
            '--no-interactive'
        ])
        
        # Click should handle type validation
        assert result.exit_code != 0 or "invalid" in result.output.lower()
    
    def test_show_invalid_number(self, runner, mock_config_manager):
        """Test showing connection with invalid number"""
        result = runner.invoke(show, ['999'])
        
        assert result.exit_code == 0
        assert "Invalid connection number" in result.output


class TestConfigCommands:
    """Test configuration-related commands"""
    
    def test_config_command(self, runner, mock_config_manager):
        """Test config command basic functionality"""
        mock_config_manager.get_setting = MagicMock(return_value="~/.ssh/id_rsa")
        
        with patch('src.cli.Confirm.ask') as mock_confirm:
            mock_confirm.return_value = False  # Don't update key
            
            result = runner.invoke(config, [])
            
            assert result.exit_code == 0
            assert "Configuration" in result.output
            assert "Default SSH Key" in result.output
    
    def test_refresh_command(self, runner, mock_config_manager):
        """Test refresh command"""
        result = runner.invoke(refresh, [])
        
        assert result.exit_code == 0
        assert "configuration refreshed" in result.output or "Regenerating" in result.output


class TestNonInteractiveMode:
    """Test CLI in non-interactive mode"""
    
    @pytest.mark.parametrize("missing_arg,expected_error", [
        (['--host', 'test.com', '--user', 'test'], "Connection name is required"),
        (['--name', 'test', '--user', 'test'], "Host is required"),
        (['--name', 'test', '--host', 'test.com'], "Username is required"),
    ])
    def test_non_interactive_missing_args(self, runner, mock_config_manager, missing_arg, expected_error):
        """Test non-interactive mode with missing required arguments"""
        args = missing_arg + ['--no-interactive']
        result = runner.invoke(add, args)
        
        assert result.exit_code == 0
        assert expected_error in result.output
    
    def test_non_interactive_complete_args(self, runner, mock_config_manager):
        """Test non-interactive mode with all required arguments"""
        result = runner.invoke(add, [
            '--name', 'complete',
            '--host', 'complete.com',
            '--user', 'completeuser',
            '--port', '22',
            '--key', '~/.ssh/id_rsa',
            '--notes', 'Complete test',
            '--no-interactive'
        ])
        
        assert result.exit_code == 0
        assert "Added connection 'complete'" in result.output
        
        # Verify all fields were set
        connections = mock_config_manager.list_connections()
        assert len(connections) == 1
        conn = connections[0]
        assert conn.name == 'complete'
        assert conn.host == 'complete.com'
        assert conn.user == 'completeuser'
        assert conn.identity_file == '~/.ssh/id_rsa'
        assert conn.notes == 'Complete test'


class TestErrorHandling:
    """Test error handling in CLI commands"""
    
    def test_uninitialized_config(self, runner):
        """Test commands when config manager is not initialized"""
        with patch('src.cli.SSHConfigManager') as mock_cm:
            manager = MagicMock()
            manager.is_initialized.return_value = False
            mock_cm.return_value = manager
            
            result = runner.invoke(add, [
                '--name', 'test',
                '--host', 'test.com',
                '--user', 'test',
                '--no-interactive'
            ])
            
            assert result.exit_code == 0
            assert "Please run 'tg init' first" in result.output
