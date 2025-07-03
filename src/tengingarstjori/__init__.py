"""Tengingarstjóri - SSH Connection Manager.

A TUI-based SSH connection manager with smart config integration.
"""

__version__ = "0.1.0"
__author__ = "Ryan"
__email__ = "ryan@example.com"
__description__ = "SSH Connection Manager with TUI interface"
__license__ = "MIT"
__url__ = "https://github.com/yourusername/tengingarstjori"

from .cli import cli
from .config_manager import SSHConfigManager

# Import main classes for easier access
from .models import SSHConnection

# Define what gets imported with "from tengingarstjori import *"
__all__ = [
    "SSHConnection",
    "SSHConfigManager",
    "cli",
    "__version__",
    "__author__",
    "__description__",
]
