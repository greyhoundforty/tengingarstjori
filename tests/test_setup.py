"""Tests for the setup wizard."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.exceptions import SetupError
from src.setup import SetupWizard, run_initial_setup


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
        """Test SetupWizard initialization."""
        wizard = SetupWizard(mock_config_manager)
        assert wizard.config_manager == mock_config_manager
        assert wizard.ssh_dir == Path.home() / ".ssh"

    def test_show_welcome_message(self, mock_config_manager):
        """Test welcome message display."""
        wizard = SetupWizard(mock_config_manager)
        # Should not raise any exceptions
        wizard._show_welcome_message()

    def test_ensure_ssh_directory_exists(self, mock_config_manager, temp_home):
        """Test SSH directory creation."""
        with patch("pathlib.Path.home", return_value=temp_home):
            wizard = SetupWizard(mock_config_manager)
            wizard._ensure_ssh_directory()

            ssh_dir = temp_home / ".ssh"
            assert ssh_dir.exists()
            assert oct(ssh_dir.stat().st_mode)[-3:] == "700"

    def test_select_from_existing_keys(self, mock_config_manager):
        """Test SSH key selection from existing keys."""
        wizard = SetupWizard(mock_config_manager)
        available_keys = ["/home/user/.ssh/id_ed25519", "/home/user/.ssh/id_rsa"]

        with patch("src.setup.Prompt.ask", return_value="1"):
            result = wizard._get_key_selection(available_keys)
            assert result == "/home/user/.ssh/id_ed25519"

        with patch("src.setup.Prompt.ask", return_value="2"):
            result = wizard._get_key_selection(available_keys)
            assert result == "/home/user/.ssh/id_rsa"

    def test_custom_key_path_selection(self, mock_config_manager):
        """Test custom SSH key path selection."""
        wizard = SetupWizard(mock_config_manager)
        available_keys = ["/home/user/.ssh/id_ed25519"]

        with (
            patch("src.setup.Prompt.ask", return_value="/custom/path"),
            patch("pathlib.Path.expanduser") as mock_expand,
            patch("pathlib.Path.exists", return_value=True),
        ):
            mock_expand.return_value = Path("/custom/path")
            result = wizard._get_key_selection(available_keys)
            assert result == "/custom/path"

    def test_invalid_key_selection_retries(self, mock_config_manager):
        """Test invalid key selection with retries."""
        wizard = SetupWizard(mock_config_manager)
        available_keys = ["/home/user/.ssh/id_ed25519"]

        with patch("src.setup.Prompt.ask", side_effect=["999", "invalid", "too_many"]):
            result = wizard._get_key_selection(available_keys)
            assert result is None  # Should give up after max attempts

    def test_handle_no_existing_keys(self, mock_config_manager):
        """Test handling when no SSH keys exist."""
        wizard = SetupWizard(mock_config_manager)

        with (
            patch("src.setup.Prompt.ask", return_value="/new/key/path"),
            patch("pathlib.Path.expanduser") as mock_expand,
            patch("pathlib.Path.exists", return_value=True),
        ):
            mock_expand.return_value = Path("/new/key/path")
            result = wizard._handle_no_existing_keys()
            assert result == "/new/key/path"

        # Test with empty response
        with patch("src.setup.Prompt.ask", return_value=""):
            result = wizard._handle_no_existing_keys()
            assert result is None

    def test_confirm_ssh_integration(self, mock_config_manager):
        """Test SSH integration confirmation."""
        wizard = SetupWizard(mock_config_manager)

        with patch("src.setup.Confirm.ask", return_value=True):
            result = wizard._confirm_ssh_integration()
            assert result is True

        with patch("src.setup.Confirm.ask", return_value=False):
            result = wizard._confirm_ssh_integration()
            assert result is False

    def test_successful_setup_run(self, mock_config_manager):
        """Test successful complete setup run."""
        wizard = SetupWizard(mock_config_manager)

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
            mock_config_manager.update_setting.assert_called_with(
                "default_identity_file", "/test/key"
            )

    def test_setup_cancelled_by_user(self, mock_config_manager):
        """Test setup cancelled by user."""
        wizard = SetupWizard(mock_config_manager)

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

        with (
            patch.object(wizard, "_show_welcome_message"),
            patch.object(wizard, "_ensure_ssh_directory"),
            patch.object(wizard, "_configure_default_ssh_key", return_value=None),
            patch.object(wizard, "_confirm_ssh_integration", return_value=True),
            patch.object(
                wizard,
                "_setup_ssh_config_integration",
                side_effect=SetupError("Test error"),
            ),
        ):
            result = wizard.run_initial_setup()
            assert result is False

    def test_unexpected_error_handling(self, mock_config_manager):
        """Test unexpected error handling."""
        wizard = SetupWizard(mock_config_manager)

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
        # Should not raise any exceptions
        wizard._show_completion_message()


class TestSetupFunctions:
    """Test module-level setup functions."""

    def test_run_initial_setup_function(self, mock_config_manager):
        """Test the run_initial_setup function."""
        with patch("src.setup.SetupWizard") as mock_wizard_class:
            mock_wizard = MagicMock()
            mock_wizard.run_initial_setup.return_value = True
            mock_wizard_class.return_value = mock_wizard

            result = run_initial_setup(mock_config_manager)

            assert result is True
            mock_wizard_class.assert_called_once_with(mock_config_manager)
            mock_wizard.run_initial_setup.assert_called_once()

    def test_configure_default_ssh_key_with_keys(self, mock_config_manager):
        """Test configuring default SSH key when keys exist."""
        wizard = SetupWizard(mock_config_manager)
        mock_config_manager.discover_ssh_keys.return_value = ["/test/key"]

        with patch.object(
            wizard, "_select_from_existing_keys", return_value="/test/key"
        ):
            result = wizard._configure_default_ssh_key()
            assert result == "/test/key"

    def test_configure_default_ssh_key_no_keys(self, mock_config_manager):
        """Test configuring default SSH key when no keys exist."""
        wizard = SetupWizard(mock_config_manager)
        mock_config_manager.discover_ssh_keys.return_value = []

        with patch.object(wizard, "_handle_no_existing_keys", return_value=None):
            result = wizard._configure_default_ssh_key()
            assert result is None

    def test_select_from_existing_keys_display(self, mock_config_manager):
        """Test that existing keys are displayed correctly."""
        wizard = SetupWizard(mock_config_manager)
        available_keys = ["/home/user/.ssh/id_ed25519"]

        with patch.object(
            wizard, "_get_key_selection", return_value="/home/user/.ssh/id_ed25519"
        ):
            result = wizard._select_from_existing_keys(available_keys)
            assert result == "/home/user/.ssh/id_ed25519"
