"""
CLI Interface for Tengingarstjóri SSH Connection Manager

Provides 'tg' commands for managing SSH connections.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path
from typing import Optional

from .config_manager import SSHConfigManager
from .models import SSHConnection
from .setup import run_initial_setup

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Tengingarstjóri - SSH Connection Manager
    
    A TUI-based SSH connection manager with smart config integration.
    """
    pass


@cli.command()
def init():
    """Initialize Tengingarstjóri and set up SSH config integration"""
    console.print(Panel("🔧 [bold blue]Tengingarstjóri Setup[/bold blue]", style="blue"))
    
    config_manager = SSHConfigManager()
    
    if config_manager.is_initialized():
        console.print("[yellow]Already initialized. Use 'tg config' to modify settings.[/yellow]")
        return
    
    run_initial_setup(config_manager)


@cli.command()
@click.option('--name', '-n', help='Connection name')
@click.option('--host', '-h', help='Host/IP address')
@click.option('--user', '-u', help='Username')
@click.option('--port', '-p', type=int, help='SSH port (default: 22)')
@click.option('--hostname', help='SSH HostName (if different from host)')
@click.option('--key', '-k', help='SSH private key path')
@click.option('--proxy-jump', help='ProxyJump configuration')
@click.option('--local-forward', help='LocalForward configuration')
@click.option('--remote-forward', help='RemoteForward configuration')
@click.option('--notes', help='Connection notes')
@click.option('--interactive/--no-interactive', '-i/-I', default=True, help='Use interactive mode for missing options')
def add(name, host, user, port, hostname, key, proxy_jump, local_forward, remote_forward, notes, interactive):
    """Add a new SSH connection
    
    Examples:
        tg add -n server1 -h 192.168.1.10 -u admin
        tg add --name myserver --host example.com --user deploy --port 2222
        tg add  # Interactive mode
    """
    config_manager = SSHConfigManager()
    
    if not config_manager.is_initialized():
        console.print("[red]Please run 'tg init' first[/red]")
        return
    
    console.print(Panel("➕ [bold green]Add SSH Connection[/bold green]", style="green"))
    
    # Handle required fields with CLI args or interactive prompts
    if not name:
        if interactive:
            name = Prompt.ask("[cyan]Connection name[/cyan]")
        else:
            console.print("[red]Connection name is required (use --name or -n)[/red]")
            return
    
    # Check for duplicates
    if config_manager.get_connection_by_name(name):
        console.print(f"[red]Connection '{name}' already exists[/red]")
        return
    
    if not host:
        if interactive:
            host = Prompt.ask("[cyan]Host/IP address[/cyan]")
        else:
            console.print("[red]Host is required (use --host or -h)[/red]")
            return
    
    if not user:
        if interactive:
            user = Prompt.ask("[cyan]Username[/cyan]")
        else:
            console.print("[red]Username is required (use --user or -u)[/red]")
            return
    
    # Port handling - default to 22 if not specified
    if port is None:
        if interactive:
            port_input = Prompt.ask("[cyan]Port[/cyan]", default="22")
            port = int(port_input)
        else:
            port = 22
    
    # Optional hostname
    if not hostname and interactive:
        hostname = Prompt.ask("[cyan]SSH HostName (if different from host)[/cyan]", default="")
        if not hostname:
            hostname = None
    
    # SSH key selection
    if not key:
        available_keys = config_manager.discover_ssh_keys()
        default_key = config_manager.get_setting("default_identity_file")
        
        if interactive and available_keys:
            console.print("\n[yellow]Available SSH keys:[/yellow]")
            for i, found_key in enumerate(available_keys, 1):
                marker = " (default)" if found_key == default_key else ""
                console.print(f"  {i}. {found_key}{marker}")
            
            key_choice = Prompt.ask(
                "[cyan]Select key (number) or enter custom path[/cyan]", 
                default="default" if default_key else ""
            )
            
            if key_choice == "default" and default_key:
                key = default_key
            elif key_choice.isdigit() and 1 <= int(key_choice) <= len(available_keys):
                key = available_keys[int(key_choice) - 1]
            elif key_choice:
                key = key_choice
            else:
                key = None
        elif not interactive and default_key:
            key = default_key
        elif interactive:
            key = Prompt.ask("[cyan]SSH key path (optional)[/cyan]", default="")
            if not key:
                key = None
    
    # Advanced options
    if interactive and not any([proxy_jump, local_forward, remote_forward]):
        if Confirm.ask("[cyan]Add advanced options?[/cyan]", default=False):
            if not proxy_jump:
                proxy_jump = Prompt.ask("[cyan]ProxyJump (optional)[/cyan]", default="")
            if not local_forward:
                local_forward = Prompt.ask("[cyan]LocalForward (optional)[/cyan]", default="")
            if not remote_forward:
                remote_forward = Prompt.ask("[cyan]RemoteForward (optional)[/cyan]", default="")
    
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
        notes=clean_option(notes)
    )
    
    if config_manager.add_connection(connection):
        console.print(f"[green]✓[/green] Added connection '{name}'")
        console.print(f"[dim]Connect with: ssh {name}[/dim]")
    else:
        console.print(f"[red]Failed to add connection '{name}'[/red]")


@cli.command()
def list():
    """List all SSH connections"""
    config_manager = SSHConfigManager()
    connections = config_manager.list_connections()
    
    if not connections:
        console.print("[yellow]No connections configured. Use 'tg add' to create one.[/yellow]")
        return
    
    table = Table(title="SSH Connections")
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Host", style="blue")
    table.add_column("User", style="green")
    table.add_column("Port", style="yellow", width=5)
    table.add_column("Key", style="magenta")
    table.add_column("Last Used", style="dim")
    
    for i, conn in enumerate(connections, 1):
        key_display = Path(conn.identity_file).name if conn.identity_file else "default"
        last_used = conn.last_used.strftime("%Y-%m-%d") if conn.last_used else "Never"
        
        table.add_row(
            str(i),
            conn.name,
            conn.host,
            conn.user,
            str(conn.port),
            key_display,
            last_used
        )
    
    console.print(table)
    console.print(f"\n[dim]Total: {len(connections)} connections[/dim]")


@cli.command()
@click.argument('connection_ref')
def show(connection_ref: str):
    """Show detailed information about a connection"""
    config_manager = SSHConfigManager()
    
    # Try to find by number or name
    if connection_ref.isdigit():
        connections = config_manager.list_connections()
        index = int(connection_ref) - 1
        if 0 <= index < len(connections):
            connection = connections[index]
        else:
            console.print(f"[red]Invalid connection number: {connection_ref}[/red]")
            return
    else:
        connection = config_manager.get_connection_by_name(connection_ref)
        if not connection:
            console.print(f"[red]Connection '{connection_ref}' not found[/red]")
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
@click.argument('connection_ref')
def remove(connection_ref: str):
    """Remove an SSH connection"""
    config_manager = SSHConfigManager()
    
    # Find connection
    connection = None
    if connection_ref.isdigit():
        connections = config_manager.list_connections()
        index = int(connection_ref) - 1
        if 0 <= index < len(connections):
            connection = connections[index]
    else:
        connection = config_manager.get_connection_by_name(connection_ref)
    
    if not connection:
        console.print(f"[red]Connection '{connection_ref}' not found[/red]")
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
    """Configure Tengingarstjóri settings"""
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
    """Fix corrupted SSH configuration"""
    config_manager = SSHConfigManager()
    
    console.print("[yellow]Fixing SSH configuration...[/yellow]")
    
    try:
        # Read current SSH config
        ssh_config_path = Path.home() / ".ssh" / "config"
        
        if ssh_config_path.exists():
            with open(ssh_config_path, 'r') as f:
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
            lines = content.split('\\n')
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
            
            cleaned_content = '\\n'.join(cleaned_lines).strip()
            
            if cleaned_content != original_content:
                # Backup
                backup_path = ssh_config_path.with_suffix('.backup-fix')
                with open(backup_path, 'w') as f:
                    f.write(original_content)
                console.print(f"[green]✓[/green] Backup saved to: {backup_path}")
                
                # Write cleaned content
                with open(ssh_config_path, 'w') as f:
                    f.write(cleaned_content)
                
                console.print("[green]✓[/green] Removed corrupted include lines")
            else:
                console.print("[yellow]No corrupted lines found[/yellow]")
        
        # Now add the correct include line
        config_manager._ensure_include_line()
        console.print("[green]✓[/green] SSH configuration fixed")
        
        # Show final config
        console.print("\n[bold]Fixed SSH config:[/bold]")
        with open(ssh_config_path, 'r') as f:
            console.print(f.read()[:300] + "...")
            
    except Exception as e:
        console.print(f"[red]Error fixing SSH config: {e}[/red]")


@cli.command()
def refresh():
    """Regenerate SSH configuration file"""
    config_manager = SSHConfigManager()
    
    console.print("[blue]Regenerating SSH configuration...[/blue]")
    
    try:
        config_manager._update_ssh_config()
        console.print("[green]✓[/green] SSH configuration refreshed")
        console.print(f"[dim]Config file: {config_manager.managed_config}[/dim]")
    except Exception as e:
        console.print(f"[red]Error refreshing config: {e}[/red]")


if __name__ == "__main__":
    cli()
