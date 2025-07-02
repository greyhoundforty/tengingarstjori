"""CLI Interface for Tengingarstjóri SSH Connection Manager.

Provides 'tg' commands for managing SSH connections.
"""

import shutil
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from .config_manager import SSHConfigManager
from .models import SSHConnection
from .setup import run_initial_setup

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Tengingarstjóri - SSH Connection Manager.

    A TUI-based SSH connection manager with smart config integration.
    """
    pass


@cli.command()
def init():
    """Initialize Tengingarstjóri and set up SSH config integration."""
    console.print(
        Panel("🔧 [bold blue]Tengingarstjóri Setup[/bold blue]", style="blue")
    )

    config_manager = SSHConfigManager()

    if config_manager.is_initialized():
        console.print(
            "[yellow]Already initialized. Use 'tg config' to modify settings.[/yellow]"
        )
        return

    # Check if SSH config file exists and create it if it doesn't
    ssh_config_path = config_manager.main_ssh_config
    if not ssh_config_path.exists():
        console.print(
            "[yellow]SSH config file does not exist. Creating it now...[/yellow]"
        )
        try:
            # Ensure the .ssh directory exists
            ssh_config_path.parent.mkdir(mode=0o700, exist_ok=True)

            # Create the config file with a timestamp comment
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(ssh_config_path, "w") as f:
                f.write(
                    f"# SSH config file created by Tengingarstjóri on {timestamp}\n\n"
                )

            # Set proper permissions
            ssh_config_path.chmod(0o600)

            console.print(
                "[green]✓[/green] Created SSH config file with proper permissions"
            )

            # Since we just created the file, make a backup of this empty file
            # This ensures reset command will work later
            backup_path = ssh_config_path.with_suffix(".backup")
            shutil.copy2(ssh_config_path, backup_path)

        except Exception as e:
            console.print(f"[red]Error creating SSH config file: {e}[/red]")
            console.print(
                "[yellow]You may need to create it manually before continuing.[/yellow]"
            )
            return

    run_initial_setup(config_manager)


def _get_required_field(
    field_name: str, value: str, interactive: bool, prompt_text: str, error_msg: str
):
    """Get required fields for connection."""
    if not value:
        if interactive:
            return Prompt.ask(prompt_text)
        else:
            console.print(f"[red]{error_msg}[/red]")
            return None
    return value


def _handle_ssh_key_selection(config_manager, key: str, interactive: bool):
    """Handle SSH key selection logic."""
    if key:
        return key

    available_keys = config_manager.discover_ssh_keys()
    default_key = config_manager.get_setting("default_identity_file")

    if interactive and available_keys:
        console.print("\n[yellow]Available SSH keys:[/yellow]")
        for i, found_key in enumerate(available_keys, 1):
            marker = " (default)" if found_key == default_key else ""
            console.print(f"  {i}. {found_key}{marker}")

        key_choice = Prompt.ask(
            "[cyan]Select key (number) or enter custom path[/cyan]",
            default="default" if default_key else "",
        )

        if key_choice == "default" and default_key:
            return default_key
        elif key_choice.isdigit() and 1 <= int(key_choice) <= len(available_keys):
            return available_keys[int(key_choice) - 1]
        elif key_choice:
            return key_choice
    elif not interactive and default_key:
        return default_key
    elif interactive:
        user_key = Prompt.ask("[cyan]SSH key path (optional)[/cyan]", default="")
        return user_key if user_key else None

    return None


def _get_advanced_options(
    interactive: bool, proxy_jump: str, local_forward: str, remote_forward: str
):
    """Get advanced SSH options if in interactive mode."""
    if not interactive or any([proxy_jump, local_forward, remote_forward]):
        return proxy_jump, local_forward, remote_forward

    if Confirm.ask("[cyan]Add advanced options?[/cyan]", default=False):
        if not proxy_jump:
            proxy_jump = Prompt.ask("[cyan]ProxyJump (optional)[/cyan]", default="")
        if not local_forward:
            local_forward = Prompt.ask(
                "[cyan]LocalForward (optional)[/cyan]", default=""
            )
        if not remote_forward:
            remote_forward = Prompt.ask(
                "[cyan]RemoteForward (optional)[/cyan]", default=""
            )

    return proxy_jump, local_forward, remote_forward


@cli.command()
@click.option("--name", "-n", help="Connection name")
@click.option("--host", "-h", help="Host/IP address")
@click.option("--user", "-u", help="Username")
@click.option("--port", "-p", type=int, help="SSH port (default: 22)")
@click.option("--hostname", help="SSH HostName (if different from host)")
@click.option("--key", "-k", help="SSH private key path")
@click.option("--proxy-jump", help="ProxyJump configuration")
@click.option("--local-forward", help="LocalForward configuration")
@click.option("--remote-forward", help="RemoteForward configuration")
@click.option("--notes", help="Connection notes")
@click.option(
    "--non-interactive",
    is_flag=True,
    default=False,
    help="Use non-interactive mode (requires all options via flags)",
)
def add(
    name,
    host,
    user,
    port,
    hostname,
    key,
    proxy_jump,
    local_forward,
    remote_forward,
    notes,
    non_interactive,
):
    """Add a new SSH connection.

    Examples:
        # Basic connections
        tg add -n server1 -h 192.168.1.10 -u admin
        tg add --name myserver --host example.com --user deploy --port 2222

        # ProxyJump examples
        tg add -n internal --host 10.0.1.100 -u admin --proxy-jump bastion.company.com
        tg add -n db-server --host 192.168.10.50 -u dbadmin --proxy-jump "jumpuser@bastion.company.com:2222"

        # Port forwarding examples
        tg add -n db-tunnel --host db.company.com -u dbuser --local-forward "3306:localhost:3306"
        tg add -n dev-server --host dev.company.com -u dev --local-forward "8080:localhost:80,3306:db:3306"

        # Complex example with multiple options
        tg add -n prod-db --host prod-db.internal -u produser \
               --proxy-jump bastion.company.com \
               --local-forward "5432:localhost:5432" \
               --key ~/.ssh/prod_key \
               --notes "Production database via bastion"

        tg add  # Interactive mode
    """
    config_manager = SSHConfigManager()

    if not config_manager.is_initialized():
        console.print("[red]Please run 'tg init' first[/red]")
        return

    console.print(
        Panel("➕ [bold green]Add SSH Connection[/bold green]", style="green")
    )

    interactive = not non_interactive

    # Get required fields
    name = _get_required_field(
        "name",
        name,
        interactive,
        "[cyan]Connection name[/cyan]",
        "Connection name is required (use --name or -n)",
    )
    if not name:
        return

    # Check for duplicates
    if config_manager.get_connection_by_name(name):
        console.print(f"[red]Connection '{name}' already exists[/red]")
        return

    host = _get_required_field(
        "host",
        host,
        interactive,
        "[cyan]Host/IP address[/cyan]",
        "Host is required (use --host or -h)",
    )
    if not host:
        return

    user = _get_required_field(
        "user",
        user,
        interactive,
        "[cyan]Username[/cyan]",
        "Username is required (use --user or -u)",
    )
    if not user:
        return

    # Port handling
    if port is None:
        if interactive:
            port_input = Prompt.ask("[cyan]Port[/cyan]", default="22")
            port = int(port_input)
        else:
            port = 22

    # Optional hostname
    if not hostname and interactive:
        hostname = Prompt.ask(
            "[cyan]SSH HostName (if different from host)[/cyan]", default=""
        )
        hostname = hostname if hostname else None

    # SSH key selection
    key = _handle_ssh_key_selection(config_manager, key, interactive)

    # Advanced options
    proxy_jump, local_forward, remote_forward = _get_advanced_options(
        interactive, proxy_jump, local_forward, remote_forward
    )

    # Notes
    if not notes and interactive:
        notes = Prompt.ask("[cyan]Notes (optional)[/cyan]", default="")

    # Clean up empty strings to None
    def clean_option(value):
        return value if value and value.strip() else None

    # Create connection
    connection = SSHConnection(
        name=name,
        host=host,
        hostname=clean_option(hostname),
        port=port,
        user=user,
        identity_file=clean_option(key),
        proxy_jump=clean_option(proxy_jump),
        local_forward=clean_option(local_forward),
        remote_forward=clean_option(remote_forward),
        notes=clean_option(notes),
    )

    if config_manager.add_connection(connection):
        console.print(f"[green]✓[/green] Added connection '{name}'")
        console.print(f"[dim]Connect with: ssh {name}[/dim]")
    else:
        console.print(f"[red]Failed to add connection '{name}'[/red]")


@cli.command()
@click.option(
    "--detailed",
    "-d",
    is_flag=True,
    help="Show detailed information including notes, proxy settings, and port forwarding",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "compact"]),
    default="table",
    help="Output format: table (default) or compact",
)
def list(detailed, format):
    """List all SSH connections.

    Examples:
        tg list                    # Basic list
        tg list --detailed         # Show all details
        tg list -d                 # Short form for detailed
        tg list -f compact         # Compact format
        tg list -d -f compact      # Detailed compact format
    """
    config_manager = SSHConfigManager()
    connections = config_manager.list_connections()

    if not connections:
        console.print(
            "[yellow]No connections configured. Use 'tg add' to create one.[/yellow]"
        )
        return

    if format == "compact":
        _display_connections_compact(connections, detailed)
    else:
        _display_connections_table(connections, detailed)

    console.print(f"\n[dim]Total: {len(connections)} connections[/dim]")


def _display_connections_table(connections, detailed=False):
    """Display connections in table format."""
    if detailed:
        # Detailed table with all information
        table = Table(title="SSH Connections (Detailed)", show_lines=True)
        table.add_column("#", style="dim", width=3)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Connection", style="blue")
        table.add_column("Advanced", style="magenta")
        table.add_column("Notes", style="yellow")
        table.add_column("Last Used", style="dim")

        for i, conn in enumerate(connections, 1):
            # Build connection string
            connection_str = f"{conn.user}@{conn.host}"
            if conn.port != 22:
                connection_str += f":{conn.port}"
            if conn.hostname and conn.hostname != conn.host:
                connection_str += f"\n[dim]SSH: {conn.hostname}[/dim]"
            if conn.identity_file:
                key_name = Path(conn.identity_file).name
                connection_str += f"\n[dim]Key: {key_name}[/dim]"

            # Build advanced options string
            advanced_options = []
            if conn.proxy_jump:
                advanced_options.append(f"[green]ProxyJump:[/green] {conn.proxy_jump}")
            if conn.local_forward:
                advanced_options.append(
                    f"[blue]LocalForward:[/blue] {conn.local_forward}"
                )
            if conn.remote_forward:
                advanced_options.append(
                    f"[red]RemoteForward:[/red] {conn.remote_forward}"
                )

            advanced_str = (
                "\n".join(advanced_options) if advanced_options else "[dim]None[/dim]"
            )

            # Format notes
            notes_str = conn.notes if conn.notes else "[dim]None[/dim]"
            if conn.notes and len(conn.notes) > 30:
                notes_str = conn.notes[:27] + "..."

            # Format last used
            last_used = (
                conn.last_used.strftime("%Y-%m-%d") if conn.last_used else "Never"
            )

            table.add_row(
                str(i),
                conn.name,
                connection_str,
                advanced_str,
                notes_str,
                last_used,
            )
    else:
        # Standard table (existing format)
        table = Table(title="SSH Connections")
        table.add_column("#", style="dim", width=3)
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Host", style="blue")
        table.add_column("User", style="green")
        table.add_column("Port", style="yellow", width=5)
        table.add_column("Key", style="magenta")
        table.add_column("Last Used", style="dim")

        for i, conn in enumerate(connections, 1):
            key_display = (
                Path(conn.identity_file).name if conn.identity_file else "default"
            )
            last_used = (
                conn.last_used.strftime("%Y-%m-%d") if conn.last_used else "Never"
            )

            table.add_row(
                str(i),
                conn.name,
                conn.host,
                conn.user,
                str(conn.port),
                key_display,
                last_used,
            )

    console.print(table)


def _display_connections_compact(connections, detailed=False):
    """Display connections in compact format."""
    console.print("[bold]SSH Connections:[/bold]\n")

    for i, conn in enumerate(connections, 1):
        # Basic connection info
        console.print(
            f"[cyan]{i:2}. {conn.name}[/cyan] - {conn.user}@{conn.host}:{conn.port}"
        )

        if detailed:
            details = []

            # SSH hostname if different
            if conn.hostname and conn.hostname != conn.host:
                details.append(f"SSH: {conn.hostname}")

            # SSH key
            if conn.identity_file:
                key_name = Path(conn.identity_file).name
                details.append(f"Key: {key_name}")

            # Advanced options
            if conn.proxy_jump:
                details.append(f"ProxyJump: {conn.proxy_jump}")
            if conn.local_forward:
                details.append(f"LocalForward: {conn.local_forward}")
            if conn.remote_forward:
                details.append(f"RemoteForward: {conn.remote_forward}")

            # Notes
            if conn.notes:
                details.append(f"Notes: {conn.notes}")

            # Last used
            last_used = (
                conn.last_used.strftime("%Y-%m-%d") if conn.last_used else "Never"
            )
            details.append(f"Last used: {last_used}")

            if details:
                for detail in details:
                    console.print(f"     [dim]{detail}[/dim]")

        console.print()  # Empty line between connections


def _find_connection_by_ref(config_manager, connection_ref: str):
    """Find connection by reference (number or name)."""
    if connection_ref.isdigit():
        connections = config_manager.list_connections()
        index = int(connection_ref) - 1
        if 0 <= index < len(connections):
            return connections[index]
        else:
            console.print(f"[red]Invalid connection number: {connection_ref}[/red]")
            return None
    else:
        connection = config_manager.get_connection_by_name(connection_ref)
        if not connection:
            console.print(f"[red]Connection '{connection_ref}' not found[/red]")
            return None
        return connection


@cli.command()
@click.argument("connection_ref")
def show(connection_ref: str):
    """Show detailed information about a connection."""
    config_manager = SSHConfigManager()

    connection = _find_connection_by_ref(config_manager, connection_ref)
    if not connection:
        return

    # Display detailed info
    console.print(Panel(f"🔗 [bold]{connection.name}[/bold]", style="blue"))

    info_table = Table(show_header=False)
    info_table.add_column("Field", style="cyan", width=15)
    info_table.add_column("Value", style="white")

    info_table.add_row("Host", connection.host)
    if connection.hostname and connection.hostname != connection.host:
        info_table.add_row("SSH HostName", connection.hostname)
    info_table.add_row("User", connection.user)
    info_table.add_row("Port", str(connection.port))

    if connection.identity_file:
        info_table.add_row("SSH Key", connection.identity_file)

    if connection.proxy_jump:
        info_table.add_row("ProxyJump", connection.proxy_jump)

    if connection.local_forward:
        info_table.add_row("LocalForward", connection.local_forward)

    if connection.remote_forward:
        info_table.add_row("RemoteForward", connection.remote_forward)

    if connection.notes:
        info_table.add_row("Notes", connection.notes)

    info_table.add_row("Created", connection.created_at.strftime("%Y-%m-%d %H:%M"))

    if connection.last_used:
        info_table.add_row("Last Used", connection.last_used.strftime("%Y-%m-%d %H:%M"))

    info_table.add_row("Use Count", str(connection.use_count))

    console.print(info_table)

    # Show SSH config block
    console.print("\n[bold]SSH Config Block:[/bold]")
    console.print(Panel(connection.to_ssh_config_block(), style="dim"))


@cli.command()
@click.argument("connection_ref")
def remove(connection_ref: str):
    """Remove an SSH connection."""
    config_manager = SSHConfigManager()

    connection = _find_connection_by_ref(config_manager, connection_ref)
    if not connection:
        return

    # Confirm deletion
    if not Confirm.ask(f"[red]Remove connection '{connection.name}'?[/red]"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    if config_manager.remove_connection(connection.id):
        console.print(f"[green]✓[/green] Removed connection '{connection.name}'")
    else:
        console.print(f"[red]Failed to remove connection '{connection.name}'[/red]")


@cli.command()
def config():
    """Configure Tengingarstjóri settings."""
    config_manager = SSHConfigManager()

    console.print(Panel("⚙️  [bold blue]Configuration[/bold blue]", style="blue"))

    # Show current settings
    console.print("[bold]Current Settings:[/bold]")
    settings_table = Table(show_header=False)
    settings_table.add_column("Setting", style="cyan")
    settings_table.add_column("Value", style="white")

    default_key = config_manager.get_setting("default_identity_file", "None")
    settings_table.add_row("Default SSH Key", default_key)

    console.print(settings_table)

    # Option to change default key
    if Confirm.ask("\n[cyan]Update default SSH key?[/cyan]"):
        available_keys = config_manager.discover_ssh_keys()

        if available_keys:
            console.print("\n[yellow]Available SSH keys:[/yellow]")
            for i, key in enumerate(available_keys, 1):
                console.print(f"  {i}. {key}")

            choice = Prompt.ask("[cyan]Select key (number) or enter custom path[/cyan]")

            if choice.isdigit() and 1 <= int(choice) <= len(available_keys):
                new_key = available_keys[int(choice) - 1]
            else:
                new_key = choice

            config_manager.update_setting("default_identity_file", new_key)
            console.print(f"[green]✓[/green] Updated default SSH key to: {new_key}")
        else:
            new_key = Prompt.ask("[cyan]Enter SSH key path[/cyan]")
            config_manager.update_setting("default_identity_file", new_key)
            console.print(f"[green]✓[/green] Updated default SSH key to: {new_key}")


@cli.command()
def fix_config():
    """Fix corrupted SSH configuration."""
    config_manager = SSHConfigManager()

    console.print("[yellow]Fixing SSH configuration...[/yellow]")

    try:
        # Read current SSH config
        ssh_config_path = Path.home() / ".ssh" / "config"

        if ssh_config_path.exists():
            with open(ssh_config_path, "r") as f:
                content = f.read()

            # Show current problematic content
            console.print("[dim]Current SSH config content:[/dim]")
            console.print(f"[dim]{content[:200]}...[/dim]")

            # Fix the content by removing literal \\n sequences
            managed_config_path = config_manager.managed_config

            # Remove all variations of corrupted include lines
            corrupted_patterns = [
                f"Include {managed_config_path}\\\\n\\\\n",
                f"Include {managed_config_path}\\\\n",
            ]

            original_content = content
            for pattern in corrupted_patterns:
                content = content.replace(pattern, "")

            # Clean up any duplicate empty lines
            lines = content.split("\n")
            cleaned_lines = []
            prev_empty = False

            for line in lines:
                if line.strip() == "":
                    if not prev_empty:
                        cleaned_lines.append(line)
                    prev_empty = True
                else:
                    cleaned_lines.append(line)
                    prev_empty = False

            cleaned_content = "\n".join(cleaned_lines).strip()

            if cleaned_content != original_content:
                # Backup
                backup_path = ssh_config_path.with_suffix(".backup-fix")
                with open(backup_path, "w") as f:
                    f.write(original_content)
                console.print(f"[green]✓[/green] Backup saved to: {backup_path}")

                # Write cleaned content
                with open(ssh_config_path, "w") as f:
                    f.write(cleaned_content)

                console.print("[green]✓[/green] Removed corrupted include lines")
            else:
                console.print("[yellow]No corrupted lines found[/yellow]")

        # Now add the correct include line
        config_manager._ensure_include_line()
        console.print("[green]✓[/green] SSH configuration fixed")

        # Show final config
        console.print("\n[bold]Fixed SSH config:[/bold]")
        with open(ssh_config_path, "r") as f:
            console.print(f.read()[:300] + "...")

    except Exception as e:
        console.print(f"[red]Error fixing SSH config: {e}[/red]")


@cli.command()
def refresh():
    """Regenerate SSH configuration file."""
    config_manager = SSHConfigManager()

    console.print("[blue]Regenerating SSH configuration...[/blue]")

    try:
        config_manager._update_ssh_config()
        console.print("[green]✓[/green] SSH configuration refreshed")
        console.print(f"[dim]Config file: {config_manager.managed_config}[/dim]")
    except Exception as e:
        console.print(f"[red]Error refreshing config: {e}[/red]")


@cli.command()
def reset():
    """Reset SSH configuration to the original state before Tengingarstjóri was installed."""
    config_manager = SSHConfigManager()

    console.print("[yellow]Preparing to reset SSH configuration...[/yellow]")

    # Check if the backup exists
    backup_path = config_manager.main_ssh_config.with_suffix(".backup")
    if not backup_path.exists():
        console.print(
            "[red]Cannot reset: Original backup not found.[/red]\n"
            "[yellow]This might mean that:\n"
            "1. You haven't run 'tg init' yet\n"
            "2. The backup file was deleted\n"
            "3. You're using a custom SSH config location[/yellow]"
        )
        return

    # Confirm with the user
    if not Confirm.ask(
        "[red]This will remove all Tengingarstjóri configuration and restore your original SSH config.[/red]\n"
        "[red]All your connections will remain in the database but won't be available in SSH config.[/red]\n"
        "Continue?",
        default=False,
    ):
        console.print("[yellow]Reset cancelled.[/yellow]")
        return

    try:
        # Make a backup of the current state just in case
        current_config_backup = config_manager.main_ssh_config.with_suffix(
            ".tengingarstjori-backup"
        )
        if config_manager.main_ssh_config.exists():
            shutil.copy2(config_manager.main_ssh_config, current_config_backup)
            console.print(
                f"[dim]Current config backed up to: {current_config_backup}[/dim]"
            )

        # Restore the original backup
        shutil.copy2(backup_path, config_manager.main_ssh_config)

        # Remove the managed config file
        if config_manager.managed_config.exists():
            config_manager.managed_config.unlink()
            console.print(
                f"[green]✓[/green] Removed managed config: {config_manager.managed_config}"
            )

        console.print(
            "[green]✓[/green] SSH configuration has been reset to its original state"
        )
        console.print(
            "[yellow]Note: Your connection database is still intact.[/yellow]"
        )
        console.print(
            "[yellow]To completely remove Tengingarstjóri, you can delete:[/yellow]"
        )
        console.print(
            f"[dim]- Configuration directory: {config_manager.config_dir}[/dim]"
        )

    except Exception as e:
        console.print(f"[red]Error resetting SSH configuration: {e}[/red]")
        console.print("[yellow]If you need to manually reset:[/yellow]")
        console.print(
            f"[dim]1. Copy {backup_path} to {config_manager.main_ssh_config}[/dim]"
        )
        console.print(f"[dim]2. Delete {config_manager.managed_config}[/dim]")


if __name__ == "__main__":
    cli()
