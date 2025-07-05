"""Tengingarstjóri - SSH Connection Manager.

A TUI-based SSH connection manager with smart config integration.
"""

__version__ = "0.1.0"

# Import main components for easier access
from .cli import cli
from .config_manager import SSHConfigManager
from .models import SSHConnection

__all__ = [
    "__version__",
    "cli",
    "SSHConfigManager",
    "SSHConnection",
]
