"""Tests for the setup wizard."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# FIXED: Use correct import paths for package structure
from tengingarstjori.exceptions import SetupError
from tengingarstjori.setup import SetupWizard, run_initial_setup


@pytest.fixture
def temp_home(tmp_path):
    """Create a temporary home directory."""
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    return home_dir


@pytest.fixture
def mock_config_manager():
    """Create a mock config manager."""
    manager = MagicMock()
    manager.discover_ssh_keys.return_value = ["/home/user/.ssh/id_ed25519"]
    manager.update_setting = MagicMock()
    manager.mark_initialized = MagicMock()
    manager._update_ssh_config = MagicMock()
    return manager


class TestSetupWizard:
    """Test the SetupWizard class."""

    def test_wizard_initialization(self, mock_config_manager):
        """Test that wizard initializes correctly."""
        wizard = SetupWizard(mock_config_manager)
        assert wizard.config_manager == mock_config_manager
        assert wizard.ssh_dir == Path.home() / ".ssh"

    def test_show_welcome_message(self, mock_config_manager):
        """Test the welcome message display."""
        wizard = SetupWizard(mock_config_manager)
        # This should not raise any exceptions
        wizard._show_welcome_message()

    def test_ensure_ssh_directory_exists(self, mock_config_manager, tmp_path):
        """Test SSH directory creation."""
        # Mock home directory
        with patch("pathlib.Path.home", return_value=tmp_path):
            wizard = SetupWizard(mock_config_manager)
            wizard._ensure_ssh_directory()

            ssh_dir = tmp_path / ".ssh"
            assert ssh_dir.exists()
            assert ssh_dir.stat().st_mode & 0o777 == 0o700

    def test_select_from_existing_keys(self, mock_config_manager):
        """Test key selection from existing keys."""
        wizard = SetupWizard(mock_config_manager)
        keys = ["/home/user/.ssh/id_ed25519", "/home/user/.ssh/id_rsa"]

        # Mock user selecting the first key
        with patch("rich.prompt.Prompt.ask", return_value="1"):
            result = wizard._get_key_selection(keys)
            assert result == "/home/user/.ssh/id_ed25519"

    def test_custom_key_path_selection(self, mock_config_manager, tmp_path):
        """Test custom key path selection."""
        wizard = SetupWizard(mock_config_manager)
        keys = ["/home/user/.ssh/id_ed25519"]

        # Create a temporary key file
        custom_key = tmp_path / "custom_key"
        custom_key.touch()

        # Mock user entering custom path
        with patch("rich.prompt.Prompt.ask", return_value=str(custom_key)):
            result = wizard._get_key_selection(keys)
            assert result == str(custom_key)

    def test_invalid_key_selection_retries(self, mock_config_manager):
        """Test that invalid selections are retried."""
        wizard = SetupWizard(mock_config_manager)
        keys = ["/home/user/.ssh/id_ed25519"]

        # Mock user entering invalid choices then giving up
        with patch(
            "rich.prompt.Prompt.ask", side_effect=["99", "invalid", "nonexistent"]
        ):
            result = wizard._get_key_selection(keys)
            assert result is None

    def test_handle_no_existing_keys(self, mock_config_manager):
        """Test handling when no SSH keys exist."""
        wizard = SetupWizard(mock_config_manager)

        # Mock user not providing a custom key
        with patch("rich.prompt.Prompt.ask", return_value=""):
            result = wizard._handle_no_existing_keys()
            assert result is None

    def test_confirm_ssh_integration(self, mock_config_manager):
        """Test SSH integration confirmation."""
        wizard = SetupWizard(mock_config_manager)

        # Test user confirming
        with patch("rich.prompt.Confirm.ask", return_value=True):
            result = wizard._confirm_ssh_integration()
            assert result is True

        # Test user declining
        with patch("rich.prompt.Confirm.ask", return_value=False):
            result = wizard._confirm_ssh_integration()
            assert result is False

    def test_successful_setup_run(self, mock_config_manager):
        """Test a successful complete setup run."""
        wizard = SetupWizard(mock_config_manager)

        # Mock all user interactions
        with (
            patch.object(wizard, "_show_welcome_message"),
            patch.object(wizard, "_ensure_ssh_directory"),
            patch.object(
                wizard, "_configure_default_ssh_key", return_value="/test/key"
            ),
            patch.object(wizard, "_confirm_ssh_integration", return_value=True),
            patch.object(wizard, "_setup_ssh_config_integration"),
            patch.object(wizard, "_mark_setup_complete"),
            patch.object(wizard, "_show_completion_message"),
        ):

            result = wizard.run_initial_setup()
            assert result is True
            mock_config_manager.update_setting.assert_called_once_with(
                "default_identity_file", "/test/key"
            )

    def test_setup_cancelled_by_user(self, mock_config_manager):
        """Test setup cancellation by user."""
        wizard = SetupWizard(mock_config_manager)

        # Mock user declining SSH integration
        with (
            patch.object(wizard, "_show_welcome_message"),
            patch.object(wizard, "_ensure_ssh_directory"),
            patch.object(wizard, "_configure_default_ssh_key", return_value=None),
            patch.object(wizard, "_confirm_ssh_integration", return_value=False),
        ):

            result = wizard.run_initial_setup()
            assert result is False

    def test_setup_error_handling(self, mock_config_manager):
        """Test setup error handling."""
        wizard = SetupWizard(mock_config_manager)

        # Mock an exception during setup
        with (
            patch.object(wizard, "_show_welcome_message"),
            patch.object(wizard, "_ensure_ssh_directory"),
            patch.object(
                wizard,
                "_configure_default_ssh_key",
                side_effect=Exception("Test error"),
            ),
        ):

            result = wizard.run_initial_setup()
            assert result is False

    def test_unexpected_error_handling(self, mock_config_manager):
        """Test handling of unexpected errors."""
        wizard = SetupWizard(mock_config_manager)

        # Mock an unexpected exception
        with patch.object(
            wizard,
            "_show_welcome_message",
            side_effect=RuntimeError("Unexpected error"),
        ):
            result = wizard.run_initial_setup()
            assert result is False

    def test_setup_ssh_config_integration_error(self, mock_config_manager):
        """Test SSH config integration error handling."""
        wizard = SetupWizard(mock_config_manager)
        mock_config_manager._update_ssh_config.side_effect = Exception("SSH error")

        with pytest.raises(SetupError):
            wizard._setup_ssh_config_integration()

    def test_mark_setup_complete(self, mock_config_manager):
        """Test marking setup as complete."""
        wizard = SetupWizard(mock_config_manager)
        wizard._mark_setup_complete()
        mock_config_manager.mark_initialized.assert_called_once()

    def test_show_completion_message(self, mock_config_manager):
        """Test completion message display."""
        wizard = SetupWizard(mock_config_manager)
        # This should not raise any exceptions
        wizard._show_completion_message()


class TestSetupFunctions:
    """Test standalone setup functions."""

    def test_run_initial_setup_function(self, mock_config_manager):
        """Test the standalone run_initial_setup function."""
        with patch("tengingarstjori.setup.SetupWizard") as mock_wizard_class:
            mock_wizard = MagicMock()
            mock_wizard.run_initial_setup.return_value = True
            mock_wizard_class.return_value = mock_wizard

            result = run_initial_setup(mock_config_manager)

            assert result is True
            mock_wizard_class.assert_called_once_with(mock_config_manager)
            mock_wizard.run_initial_setup.assert_called_once()

    def test_configure_default_ssh_key_with_keys(self, mock_config_manager):
        """Test SSH key configuration when keys exist."""
        wizard = SetupWizard(mock_config_manager)

        # Mock discovering keys and user selection
        with patch.object(
            wizard, "_select_from_existing_keys", return_value="/selected/key"
        ):
            result = wizard._configure_default_ssh_key()
            assert result == "/selected/key"

    def test_configure_default_ssh_key_no_keys(self, mock_config_manager):
        """Test SSH key configuration when no keys exist."""
        mock_config_manager.discover_ssh_keys.return_value = []
        wizard = SetupWizard(mock_config_manager)

        # Mock handling no existing keys
        with patch.object(wizard, "_handle_no_existing_keys", return_value=None):
            result = wizard._configure_default_ssh_key()
            assert result is None

    def test_select_from_existing_keys_display(self, mock_config_manager):
        """Test that existing keys are displayed properly."""
        wizard = SetupWizard(mock_config_manager)
        keys = ["/home/user/.ssh/id_ed25519"]

        # Mock user selection and test the display method
        with patch("rich.prompt.Prompt.ask", return_value="1"):
            result = wizard._select_from_existing_keys(keys)
            assert result == "/home/user/.ssh/id_ed25519"
