"""
Initial setup wizard for Tengingarstjóri
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path

console = Console()


def run_initial_setup(config_manager):
    """Run the initial setup wizard"""
    
    console.print("\\n[bold blue]Welcome to Tengingarstjóri![/bold blue]")
    console.print("Let's set up your SSH connection manager.\\n")
    
    # Check SSH directory
    ssh_dir = Path.home() / ".ssh"
    if not ssh_dir.exists():
        console.print("[yellow]Creating ~/.ssh directory...[/yellow]")
        ssh_dir.mkdir(mode=0o700, exist_ok=True)
    
    # Discover existing SSH keys
    available_keys = config_manager.discover_ssh_keys()
    
    if available_keys:
        console.print("[green]Found existing SSH keys:[/green]")
        for key in available_keys:
            console.print(f"  • {key}")
        
        console.print("\\n[cyan]Select a default SSH key for new connections:[/cyan]")
        for i, key in enumerate(available_keys, 1):
            console.print(f"  {i}. {key}")
        
        while True:
            choice = Prompt.ask(
                "[cyan]Choose default key (number) or enter custom path[/cyan]",
                default="1"
            )
            
            if choice.isdigit() and 1 <= int(choice) <= len(available_keys):
                default_key = available_keys[int(choice) - 1]
                break
            elif choice and Path(choice).exists():
                default_key = choice
                break
            else:
                console.print("[red]Invalid choice. Try again.[/red]")
    else:
        console.print("[yellow]No SSH keys found in ~/.ssh/[/yellow]")
        console.print("You may want to generate one with: [dim]ssh-keygen -t ed25519[/dim]\\n")
        
        default_key = Prompt.ask(
            "[cyan]Enter default SSH key path (optional)[/cyan]",
            default=""
        )
        
        if not default_key:
            default_key = None
    
    # Save default key setting
    if default_key:
        config_manager.update_setting("default_identity_file", default_key)
        console.print(f"[green]✓[/green] Set default SSH key: {default_key}")
    
    # Explain SSH config integration
    console.print("\\n[bold yellow]SSH Config Integration[/bold yellow]")
    console.print("Tengingarstjóri will:")
    console.print("  • Create a managed config file: ~/.ssh/config.tengingarstjóri")
    console.print("  • Add one include line to your main SSH config")
    console.print("  • Keep your existing SSH config untouched")
    
    if not Confirm.ask("\\n[cyan]Proceed with SSH config integration?[/cyan]", default=True):
        console.print("[yellow]Setup cancelled[/yellow]")
        return
    
    # Set up SSH config integration
    try:
        # This will create the managed config and add the include line
        config_manager._update_ssh_config()
        console.print("[green]✓[/green] SSH config integration complete")
    except Exception as e:
        console.print(f"[red]Error setting up SSH config: {e}[/red]")
        return
    
    # Mark as initialized
    config_manager.mark_initialized()
    
    # Show completion message
    console.print("\\n" + "="*50)
    console.print(Panel(
        "[green]✓ Setup Complete![/green]\\n\\n"
        "Tengingarstjóri is ready to use!\\n\\n"
        "Next steps:\\n"
        "• Add connections: [bold]tg add[/bold]\\n"
        "• List connections: [bold]tg list[/bold]\\n"
        "• Get help: [bold]tg --help[/bold]",
        title="🎉 Welcome to Tengingarstjóri",
        style="green"
    ))
