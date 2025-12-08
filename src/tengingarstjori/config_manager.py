"""SSH Configuration Manager for Tengingarstjóri.

Handles reading/writing SSH configurations without disrupting existing setup.
"""

import contextlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import SSHConnection


class SSHConfigManager:
    """Manages SSH configurations and integration."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize SSH config manager with configuration directory."""
        self.config_dir = config_dir or Path.home() / ".tengingarstjori"
        self.ssh_dir = Path.home() / ".ssh"
        self.main_ssh_config = self.ssh_dir / "config"
        self.managed_config = self.ssh_dir / "config.tengingarstjori"
        self.connections_file = self.config_dir / "connections.json"
        self.settings_file = self.config_dir / "settings.json"

        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.ssh_dir.mkdir(mode=0o700, exist_ok=True)

        self.connections: List[SSHConnection] = []
        self.settings: Dict[str, Any] = {}

        self._load_data()

    def _load_data(self) -> None:
        """Load connections and settings from disk."""
        # Load connections
        if self.connections_file.exists():
            try:
                with open(self.connections_file, "r") as f:
                    data = json.load(f)
                    self.connections = [SSHConnection(**conn) for conn in data]
            except Exception as e:
                print(f"Error loading connections: {e}")
                self.connections = []

        # Load settings
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r") as f:
                    self.settings = json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.settings = {}

    def _save_connections(self) -> None:
        """Save connections to disk."""
        try:
            with open(self.connections_file, "w") as f:
                json.dump(
                    [conn.model_dump() for conn in self.connections],
                    f,
                    indent=2,
                    default=str,
                )
        except Exception as e:
            print(f"Error saving connections: {e}")

    def _save_settings(self) -> None:
        """Save settings to disk."""
        try:
            with open(self.settings_file, "w") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def _update_ssh_config(self) -> None:
        """Update the managed SSH config file and ensure inclusion."""
        try:
            # Write managed config
            with open(self.managed_config, "w") as f:
                f.write("# Tengingarstjori SSH Connections\n")
                f.write(f"# Generated on {datetime.now().isoformat()}\n")
                f.write("# Do not edit manually - use 'tg' commands\n\n")

                for conn in self.connections:
                    f.write(conn.to_ssh_config_block())
                    f.write("\n")

            # Ensure include line exists in main config
            self._ensure_include_line()

        except Exception as e:
            print(f"Error updating SSH config: {e}")

    def _ensure_include_line(self) -> None:
        """Ensure the Include line exists in the main SSH config."""
        include_line = f"Include {self.managed_config}"

        # Read existing config
        existing_content = ""
        if self.main_ssh_config.exists():
            with open(self.main_ssh_config, "r") as f:
                existing_content = f.read()

        # Remove any corrupted include lines with literal \n characters
        corrupted_patterns = [
            f"Include {self.managed_config}\\n\\n",
            f"Include {self.managed_config}\\n",
        ]

        for pattern in corrupted_patterns:
            existing_content = existing_content.replace(pattern, "")

        # Check if clean include line already exists
        if include_line in existing_content:
            return

        # Backup existing config
        if self.main_ssh_config.exists():
            backup_path = self.main_ssh_config.with_suffix(".backup")
            shutil.copy2(self.main_ssh_config, backup_path)
            print(f"SSH config backed up to {backup_path}")

        # Add include line at the top
        new_content = f"{include_line}\n\n{existing_content.strip()}\n"

        with open(self.main_ssh_config, "w") as f:
            f.write(new_content)

        print(f"Added include line to {self.main_ssh_config}")

    def discover_ssh_keys(self) -> List[str]:
        """Discover existing SSH keys."""
        key_patterns = ["id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"]
        found_keys = []

        for pattern in key_patterns:
            key_path = self.ssh_dir / pattern
            if key_path.exists():
                found_keys.append(str(key_path))

        # Look for other private keys
        for key_file in self.ssh_dir.glob("*"):
            if (
                key_file.is_file()
                and not key_file.suffix
                and key_file.name not in key_patterns
            ):
                # Check if it looks like a private key
                with contextlib.suppress(OSError, ValueError), open(key_file, "r") as f:
                    first_line = f.readline().strip()
                    if "PRIVATE KEY" in first_line:
                        found_keys.append(str(key_file))

        return found_keys

    def add_connection(self, connection: SSHConnection) -> bool:
        """Add a new SSH connection."""
        try:
            # Check for duplicate names
            if any(conn.name == connection.name for conn in self.connections):
                return False

            self.connections.append(connection)
            self._save_connections()
            self._update_ssh_config()
            return True
        except Exception as e:
            print(f"Error adding connection: {e}")
            return False

    def remove_connection(self, connection_id: str) -> bool:
        """Remove an SSH connection."""
        try:
            original_count = len(self.connections)
            self.connections = [c for c in self.connections if c.id != connection_id]

            if len(self.connections) < original_count:
                self._save_connections()
                self._update_ssh_config()
                return True
            return False
        except Exception as e:
            print(f"Error removing connection: {e}")
            return False

    def update_connection(self, connection: SSHConnection) -> bool:
        """Update an existing SSH connection."""
        try:
            for i, conn in enumerate(self.connections):
                if conn.id == connection.id:
                    self.connections[i] = connection
                    self._save_connections()
                    self._update_ssh_config()
                    return True
            return False
        except Exception as e:
            print(f"Error updating connection: {e}")
            return False

    def get_connection(self, connection_id: str) -> Optional[SSHConnection]:
        """Get a connection by ID."""
        for conn in self.connections:
            if conn.id == connection_id:
                return conn
        return None

    def get_connection_by_name(self, name: str) -> Optional[SSHConnection]:
        """Get a connection by name."""
        for conn in self.connections:
            if conn.name == name:
                return conn
        return None

    def list_connections(self) -> List[SSHConnection]:
        """Get all connections."""
        return self.connections.copy()

    def update_setting(self, key: str, value: Any) -> None:
        """Update a setting."""
        self.settings[key] = value
        self._save_settings()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value."""
        return self.settings.get(key, default)

    def is_initialized(self) -> bool:
        """Check if the system has been initialized."""
        result = self.get_setting("initialized", False)
        return bool(result) if isinstance(result, bool) else False

    def mark_initialized(self) -> None:
        """Mark the system as initialized."""
        self.update_setting("initialized", True)
        self.update_setting("initialized_at", datetime.now().isoformat())
