"""Initial setup wizard for Tengingarstjóri.

This module provides the initial setup wizard with proper string handling,
error management, and improved user experience.
"""

import logging
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

console = Console()
logger = logging.getLogger(__name__)


class SetupError(Exception):
    """Exception raised during setup process."""

    pass


class SetupWizard:
    """
    Handles the initial setup process for Tengingarstjóri.

    This class encapsulates all setup logic, making it easier to test
    and maintain compared to the original function-based approach.
    """

    def __init__(self, config_manager):
        """Initialize the setup wizard with a config manager instance."""
        self.config_manager = config_manager
        self.ssh_dir = Path.home() / ".ssh"

    def run_initial_setup(self) -> bool:
        """
        Run the complete initial setup wizard.

        Returns:
            bool: True if setup completed successfully, False otherwise
        """
        try:
            self._show_welcome_message()
            self._ensure_ssh_directory()

            default_key = self._configure_default_ssh_key()
            if default_key:
                self.config_manager.update_setting("default_identity_file", default_key)
                console.print(f"[green]✓[/green] Set default SSH key: {default_key}")

            if not self._confirm_ssh_integration():
                console.print("[yellow]Setup cancelled[/yellow]")
                return False

            self._setup_ssh_config_integration()
            self._mark_setup_complete()
            self._show_completion_message()

            return True

        except SetupError as e:
            console.print(f"[red]Setup failed: {e}[/red]")
            return False
        except Exception as e:
            logger.exception("Unexpected error during setup")
            console.print(f"[red]Unexpected error during setup: {e}[/red]")
            return False

    def _show_welcome_message(self) -> None:
        """Display the welcome message and introduction."""
        # Fixed: Removed escaped backslashes - these should be actual newlines
        console.print("\n[bold blue]Welcome to Tengingarstjóri![/bold blue]")
        console.print("Let's set up your SSH connection manager.\n")

    def _ensure_ssh_directory(self) -> None:
        """Ensure the SSH directory exists with proper permissions."""
        if not self.ssh_dir.exists():
            console.print("[yellow]Creating ~/.ssh directory...[/yellow]")
            self.ssh_dir.mkdir(mode=0o700, exist_ok=True)
            logger.info("Created SSH directory with secure permissions")

    def _configure_default_ssh_key(self) -> Optional[str]:
        """
        Configure the default SSH key for new connections.

        Returns:
            Optional[str]: Path to the selected default SSH key, or None
        """
        available_keys = self.config_manager.discover_ssh_keys()

        if available_keys:
            return self._select_from_existing_keys(available_keys)
        else:
            return self._handle_no_existing_keys()

    def _select_from_existing_keys(self, available_keys: List[str]) -> Optional[str]:
        """
        Allow user to select from existing SSH keys.

        Args:
            available_keys: List of discovered SSH key paths

        Returns:
            Optional[str]: Selected key path or None
        """
        console.print("[green]Found existing SSH keys:[/green]")
        for key in available_keys:
            console.print(f"  • {key}")

        # Fixed: Removed escaped backslashes
        console.print("\n[cyan]Select a default SSH key for new connections:[/cyan]")
        for i, key in enumerate(available_keys, 1):
            console.print(f"  {i}. {key}")

        return self._get_key_selection(available_keys)

    def _get_key_selection(self, available_keys: List[str]) -> Optional[str]:
        """
        Get the user's key selection with validation.

        Args:
            available_keys: List of available SSH keys

        Returns:
            Optional[str]: Selected key path or None
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            choice = Prompt.ask(
                "[cyan]Choose default key (number) or enter custom path[/cyan]",
                default="1",
            )

            # Try to parse as number
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(available_keys):
                    return available_keys[index]

            # Try as custom path
            if choice and Path(choice).expanduser().exists():
                return str(Path(choice).expanduser())

            if attempt < max_attempts - 1:
                console.print(
                    f"[red]Invalid choice. {max_attempts - attempt - 1} attempts remaining.[/red]"
                )
            else:
                console.print(
                    "[red]Too many invalid attempts. Skipping default key setup.[/red]"
                )

        return None

    def _handle_no_existing_keys(self) -> Optional[str]:
        """
        Handle the case where no SSH keys are found.

        Returns:
            Optional[str]: Custom key path or None
        """
        console.print("[yellow]No SSH keys found in ~/.ssh/[/yellow]")
        # Fixed: Removed escaped backslashes
        console.print(
            "You may want to generate one with: [dim]ssh-keygen -t ed25519[/dim]\n"
        )

        default_key = Prompt.ask(
            "[cyan]Enter default SSH key path (optional)[/cyan]", default=""
        )

        if default_key and Path(default_key).expanduser().exists():
            return str(Path(default_key).expanduser())

        return None

    def _confirm_ssh_integration(self) -> bool:
        """
        Explain SSH config integration and get user confirmation.

        Returns:
            bool: True if user confirms, False otherwise
        """
        # Fixed: Removed escaped backslashes
        console.print("\n[bold yellow]SSH Config Integration[/bold yellow]")
        console.print("Tengingarstjóri will:")
        console.print("  • Create a managed config file: ~/.ssh/config.tengingarstjóri")
        console.print("  • Add one include line to your main SSH config")
        console.print("  • Keep your existing SSH config untouched")

        return Confirm.ask(
            "\n[cyan]Proceed with SSH config integration?[/cyan]", default=True
        )

    def _setup_ssh_config_integration(self) -> None:
        """Set up SSH config integration with error handling."""
        try:
            # This will create the managed config and add the include line
            self.config_manager._update_ssh_config()
            console.print("[green]✓[/green] SSH config integration complete")
            logger.info("SSH config integration completed successfully")
        except Exception as e:
            logger.error(f"SSH config integration failed: {e}")
            raise SetupError(f"Failed to set up SSH config integration: {e}")

    def _mark_setup_complete(self) -> None:
        """Mark the setup as completed in the configuration."""
        self.config_manager.mark_initialized()
        logger.info("Setup marked as complete")

    def _show_completion_message(self) -> None:
        """Display the setup completion message with next steps."""
        # Fixed: Removed escaped backslashes
        console.print("\n" + "=" * 50)
        console.print(
            Panel(
                "[green]✓ Setup Complete![/green]\n\n"
                "Tengingarstjóri is ready to use!\n\n"
                "Next steps:\n"
                "• Add connections: [bold]tg add[/bold]\n"
                "• List connections: [bold]tg list[/bold]\n"
                "• Get help: [bold]tg --help[/bold]",
                title="🎉 Welcome to Tengingarstjóri",
                style="green",
            )
        )


def run_initial_setup(config_manager) -> bool:
    """
    Legacy function wrapper for backward compatibility.

    Args:
        config_manager: SSH configuration manager instance

    Returns:
        bool: True if setup completed successfully, False otherwise
    """
    wizard = SetupWizard(config_manager)
    return wizard.run_initial_setup()
