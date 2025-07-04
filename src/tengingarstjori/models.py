"""SSH Connection model for Tengingarstjóri."""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("local_forward")
    @classmethod
    def validate_local_forward(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and fix LocalForward syntax.

        Converts formats like:
        - "3306:localhost:3306" -> "3306 localhost:3306"
        - "8080:localhost:80,3000:localhost:3000" -> Multiple LocalForward entries

        Args:
            v: Raw LocalForward string from user input

        Returns:
            Corrected LocalForward string with proper SSH syntax

        Raises:
            ValueError: If the format is invalid
        """
        if not v:
            return v

        return cls._normalize_port_forward(v, "LocalForward")

    @field_validator("remote_forward")
    @classmethod
    def validate_remote_forward(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate and fix RemoteForward syntax.

        Args:
            v: Raw RemoteForward string from user input

        Returns:
            Corrected RemoteForward string with proper SSH syntax

        Raises:
            ValueError: If the format is invalid
        """
        if not v:
            return v

        return cls._normalize_port_forward(v, "RemoteForward")

    @staticmethod
    def _normalize_port_forward(forward_str: str, forward_type: str) -> str:
        """
        Normalize port forwarding syntax to proper SSH config format.

        Handles multiple formats and converts them to proper SSH syntax:
        - "3306:localhost:3306" -> "3306 localhost:3306"
        - "127.0.0.1:3306:localhost:3306" -> "127.0.0.1:3306 localhost:3306"
        - "3306:db.internal:3306" -> "3306 db.internal:3306"
        - Multiple forwards separated by commas

        Args:
            forward_str: Raw port forward string
            forward_type: "LocalForward" or "RemoteForward" for error messages

        Returns:
            Normalized string with proper SSH syntax

        Raises:
            ValueError: If the format cannot be parsed
        """
        if not forward_str or not forward_str.strip():
            return ""

        # Split multiple forwards by comma
        forwards = [f.strip() for f in forward_str.split(",") if f.strip()]
        normalized_forwards = []

        for forward in forwards:
            normalized_forward = SSHConnection._normalize_single_forward(
                forward, forward_type
            )
            normalized_forwards.append(normalized_forward)

        return ",".join(normalized_forwards)

    @staticmethod
    def _normalize_single_forward(forward: str, forward_type: str) -> str:
        """
        Normalize a single port forward entry.

        Args:
            forward: Single port forward string (e.g., "3306:localhost:3306")
            forward_type: "LocalForward" or "RemoteForward" for error messages

        Returns:
            Normalized single forward entry

        Raises:
            ValueError: If the format is invalid
        """
        # Remove extra whitespace
        forward = forward.strip()

        # Reject completely invalid formats early
        if not forward or forward.count(":") < 1:
            raise ValueError(
                f"Invalid {forward_type} format: '{forward}'. "
                f"Must contain at least one colon"
            )

        # Pattern for different forward formats:
        # 1. "port:target:port" -> "port target:port"
        # 2. "bind_address:port:target:port" -> "bind_address:port target:port"
        # 3. "port target:port" (already correct)
        # 4. "bind_address:port target:port" (already correct)

        # Check if already in correct format (contains space)
        if " " in forward:
            # Validate that it's in correct format: "local_spec target:port"
            parts = forward.split(" ", 1)
            if len(parts) == 2:
                local_part, remote_part = parts

                # Validate remote part has format "host:port"
                if ":" in remote_part:
                    remote_host, remote_port = remote_part.rsplit(":", 1)
                    if not remote_port.isdigit():
                        raise ValueError(
                            f"Invalid {forward_type} format: '{forward}'. "
                            f"Remote port must be numeric, got '{remote_port}'"
                        )
                    return forward  # Already in correct format
                else:
                    raise ValueError(
                        f"Invalid {forward_type} format: '{forward}'. "
                        f"Remote part must be 'host:port'"
                    )
            else:
                raise ValueError(
                    f"Invalid {forward_type} format: '{forward}'. "
                    f"When using space separator, format must be 'local_spec remote_host:remote_port'"
                )

        # Handle colon-separated format that needs conversion
        colon_parts = forward.split(":")

        if len(colon_parts) == 3:
            # Format: "local_port:remote_host:remote_port"
            local_port, remote_host, remote_port = colon_parts

            # Validate local_port is numeric
            if not local_port.isdigit():
                raise ValueError(
                    f"Invalid {forward_type} format: '{forward}'. "
                    f"Local port must be numeric, got '{local_port}'"
                )

            # Validate remote_port is numeric
            if not remote_port.isdigit():
                raise ValueError(
                    f"Invalid {forward_type} format: '{forward}'. "
                    f"Remote port must be numeric, got '{remote_port}'"
                )

            # Validate remote_host is not empty
            if not remote_host.strip():
                raise ValueError(
                    f"Invalid {forward_type} format: '{forward}'. "
                    f"Remote host cannot be empty"
                )

            return f"{local_port} {remote_host}:{remote_port}"

        elif len(colon_parts) == 4:
            # Format: "bind_address:local_port:remote_host:remote_port"
            bind_addr, local_port, remote_host, remote_port = colon_parts

            # Validate ports are numeric
            if not local_port.isdigit():
                raise ValueError(
                    f"Invalid {forward_type} format: '{forward}'. "
                    f"Local port must be numeric, got '{local_port}'"
                )

            if not remote_port.isdigit():
                raise ValueError(
                    f"Invalid {forward_type} format: '{forward}'. "
                    f"Remote port must be numeric, got '{remote_port}'"
                )

            # Validate components are not empty
            if not bind_addr.strip():
                raise ValueError(
                    f"Invalid {forward_type} format: '{forward}'. "
                    f"Bind address cannot be empty"
                )

            if not remote_host.strip():
                raise ValueError(
                    f"Invalid {forward_type} format: '{forward}'. "
                    f"Remote host cannot be empty"
                )

            return f"{bind_addr}:{local_port} {remote_host}:{remote_port}"

        else:
            raise ValueError(
                f"Invalid {forward_type} format: '{forward}'. "
                f"Expected formats: 'local_port:remote_host:remote_port' or "
                f"'bind_address:local_port:remote_host:remote_port' or "
                f"'local_spec remote_host:remote_port'"
            )

    def to_ssh_config_block(self) -> str:
        """
        Generate SSH config block for this connection.

        Creates a properly formatted SSH config block with all connection
        parameters, including properly formatted port forwarding directives.

        Returns:
            SSH configuration block as string
        """
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

        # Handle LocalForward - support multiple forwards
        if self.local_forward:
            forwards = [f.strip() for f in self.local_forward.split(",") if f.strip()]
            for forward in forwards:
                lines.append(f"    LocalForward {forward}")

        # Handle RemoteForward - support multiple forwards
        if self.remote_forward:
            forwards = [f.strip() for f in self.remote_forward.split(",") if f.strip()]
            for forward in forwards:
                lines.append(f"    RemoteForward {forward}")

        # Extra options
        for key, value in self.extra_options.items():
            lines.append(f"    {key} {value}")

        # Add comment with notes if present
        if self.notes:
            lines.insert(1, f"    # {self.notes}")

        return "\n".join(lines) + "\n"

    def update_usage(self):
        """Update usage statistics when connection is used."""
        self.last_used = datetime.now()
        self.use_count += 1
