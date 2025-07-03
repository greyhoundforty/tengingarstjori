"""SSH Connection model for Tengingarstjóri."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SSHConnection(BaseModel):
    """Represents an SSH connection configuration."""

    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Display name for the connection")
    host: str = Field(..., description="Hostname or IP address")
    hostname: Optional[str] = Field(
        None, description="SSH config hostname (if different from host)"
    )
    port: int = Field(default=22, description="SSH port")
    user: str = Field(..., description="Username for SSH")
    identity_file: Optional[str] = Field(None, description="Path to SSH private key")
    proxy_jump: Optional[str] = Field(None, description="ProxyJump configuration")
    local_forward: Optional[str] = Field(None, description="LocalForward configuration")
    remote_forward: Optional[str] = Field(
        None, description="RemoteForward configuration"
    )
    extra_options: dict = Field(
        default_factory=dict, description="Additional SSH options"
    )
    notes: Optional[str] = Field(None, description="User notes")
    tags: list[str] = Field(default_factory=list, description="Organization tags")
    created_at: datetime = Field(default_factory=datetime.now)
    last_used: Optional[datetime] = Field(None, description="Last connection time")
    use_count: int = Field(default=0, description="Number of times connected")

    def to_ssh_config_block(self) -> str:
        """Generate SSH config block for this connection."""
        lines = [f"Host {self.name}"]

        # Core connection details
        if self.hostname:
            lines.append(f"    HostName {self.hostname}")
        else:
            lines.append(f"    HostName {self.host}")

        lines.append(f"    User {self.user}")

        if self.port != 22:
            lines.append(f"    Port {self.port}")

        if self.identity_file:
            lines.append(f"    IdentityFile {self.identity_file}")

        # Advanced options
        if self.proxy_jump:
            lines.append(f"    ProxyJump {self.proxy_jump}")

        if self.local_forward:
            lines.append(f"    LocalForward {self.local_forward}")

        if self.remote_forward:
            lines.append(f"    RemoteForward {self.remote_forward}")

        # Extra options
        for key, value in self.extra_options.items():
            lines.append(f"    {key} {value}")

        # Add comment with notes if present
        if self.notes:
            lines.insert(1, f"    # {self.notes}")

        return "\n".join(lines) + "\n"

    def update_usage(self):
        """Update usage statistics."""
        self.last_used = datetime.now()
        self.use_count += 1
