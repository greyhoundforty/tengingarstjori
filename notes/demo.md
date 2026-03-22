# Tengingarstjóri CLI Demo

*2026-03-22T08:09:55Z by Showboat 0.6.1*
<!-- showboat-id: e0ce2255-807d-49d1-838b-9b920c2df8be -->

Tengingarstjóri (tg) is a CLI SSH connection manager. This demo walks through the key commands using a live session.

## Version and Help

First, confirm the installed version and explore top-level help.

```bash
tg --version
```

```output
tg, version 0.1.0
```

```bash
tg --help
```

```output
Usage: tg [OPTIONS] COMMAND [ARGS]...

  Tengingarstjóri - SSH Connection Manager.

  A TUI-based SSH connection manager with smart config integration.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  add           Add a new SSH connection.
  config        Configure Tengingarstjóri settings.
  fix-config    Fix corrupted SSH configuration.
  fix-forwards  Fix LocalForward and RemoteForward syntax in existing...
  init          Initialize Tengingarstjóri and set up SSH config...
  list          List all SSH connections.
  refresh       Regenerate SSH configuration file.
  remove        Remove an SSH connection.
  reset         Reset SSH configuration to the original state before...
  show          Show detailed information about a connection.
  update        Update an existing SSH connection.
  validate      Validate SSH configuration syntax for all connections.
```

## Listing Connections

Use `tg list` to see all managed SSH connections. With no connections added yet, the output reflects the empty state.

```bash
tg list
```

```output
                            SSH Connections                            
┏━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ #   ┃ Name     ┃ Host           ┃ User ┃ Port  ┃ Key    ┃ Last Used ┃
┡━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ kuiper   │ 23.95.242.52   │ ryan │ 22    │ id_rsa │ Never     │
│ 2   │ charon   │ 159.65.243.4   │ ryan │ 22    │ id_rsa │ Never     │
│ 3   │ callisto │ 192.168.50.96  │ ryan │ 3356  │ id_rsa │ Never     │
│ 4   │ firefly  │ 192.168.50.151 │ ryan │ 22    │ id_rsa │ Never     │
│ 5   │ hyperion │ 192.168.50.200 │ ryan │ 22    │ id_rsa │ Never     │
│ 6   │ pluto    │ 107.173.38.148 │ ryan │ 22    │ id_rsa │ Never     │
└─────┴──────────┴────────────────┴──────┴───────┴────────┴───────────┘

Total: 6 connections
```

## Adding a Connection

`tg add` accepts flags for host, user, port, and SSH key. Here we add a demo bastion server.

```bash
tg add --non-interactive -n demo-bastion -h bastion.example.com -u deploy -p 22 -k ~/.ssh/id_rsa --notes 'Demo bastion server'
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ➕ Add SSH Connection                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Added connection 'demo-bastion'
Connect with: ssh demo-bastion
```

## Showing Connection Details

`tg show <name>` prints all stored fields for a single connection, including key, port, proxy jump, and notes.

```bash
tg show demo-bastion
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ 🔗 demo-bastion                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
┌─────────────────┬─────────────────────────┐
│ Host            │ bastion.example.com     │
│ User            │ deploy                  │
│ Port            │ 22                      │
│ SSH Key         │ /Users/ryan/.ssh/id_rsa │
│ Notes           │ Demo bastion server     │
│ Created         │ 2026-03-22 04:10        │
│ Use Count       │ 0                       │
└─────────────────┴─────────────────────────┘

SSH Config Block:
╭──────────────────────────────────────────────────────────────────────────────╮
│ Host demo-bastion                                                            │
│     # Demo bastion server                                                    │
│     HostName bastion.example.com                                             │
│     User deploy                                                              │
│     IdentityFile /Users/ryan/.ssh/id_rsa                                     │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Adding a Connection with ProxyJump

Connections that route through a bastion host use `--proxy-jump`. The generated SSH config block shows the `ProxyJump` directive automatically.

```bash
tg add --non-interactive -n demo-internal -h 10.0.1.50 -u admin --proxy-jump demo-bastion --notes 'Internal host via bastion'
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ➕ Add SSH Connection                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Added connection 'demo-internal'
Connect with: ssh demo-internal
```

```bash
tg show demo-internal
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ 🔗 demo-internal                                                             │
╰──────────────────────────────────────────────────────────────────────────────╯
┌─────────────────┬───────────────────────────┐
│ Host            │ 10.0.1.50                 │
│ User            │ admin                     │
│ Port            │ 22                        │
│ SSH Key         │ /Users/ryan/.ssh/id_rsa   │
│ ProxyJump       │ demo-bastion              │
│ Notes           │ Internal host via bastion │
│ Created         │ 2026-03-22 04:10          │
│ Use Count       │ 0                         │
└─────────────────┴───────────────────────────┘

SSH Config Block:
╭──────────────────────────────────────────────────────────────────────────────╮
│ Host demo-internal                                                           │
│     # Internal host via bastion                                              │
│     HostName 10.0.1.50                                                       │
│     User admin                                                               │
│     IdentityFile /Users/ryan/.ssh/id_rsa                                     │
│     ProxyJump demo-bastion                                                   │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## Updating a Connection

`tg update` patches individual fields on an existing connection without re-entering everything.

```bash
tg update demo-bastion --port 2222 --non-interactive
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ✏️  Update SSH Connection                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Updated connection 'demo-bastion'
  port: 2222
```

## Validating SSH Configuration

`tg validate` checks the syntax of every connection's generated SSH config block and reports any issues.

```bash
tg validate
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ 🔍 SSH Configuration Validation                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

All configurations are valid!
```

## Refreshing the SSH Config File

`tg refresh` regenerates `~/.ssh/config.tengingarstjori` from the stored connections JSON. Useful after manual edits or after `tg update`.

```bash
tg refresh
```

```output
Regenerating SSH configuration...
✓ SSH configuration refreshed
Config file: /Users/ryan/.ssh/config.tengingarstjori
```

## Viewing App Configuration

`tg config` shows current application settings such as the connections file path and SSH config path.

```bash
tg config
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ⚙️  Configuration                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
Current Settings:
┌─────────────────┬─────────────────────────┐
│ Default SSH Key │ /Users/ryan/.ssh/id_rsa │
└─────────────────┴─────────────────────────┘

Update default SSH key? [y/n]: Configuration display completed (non-interactive mode)
```

## Removing a Connection

`tg remove` deletes a connection by name and updates the SSH config file.

```bash
tg remove demo-internal --force && tg remove demo-bastion --force
```

```output
✓ Removed connection 'demo-internal'
✓ Removed connection 'demo-bastion'
```

After removal, `tg list` confirms the demo connections are gone and the original set is intact.

```bash
tg list
```

```output
                            SSH Connections                            
┏━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━┓
┃ #   ┃ Name     ┃ Host           ┃ User ┃ Port  ┃ Key    ┃ Last Used ┃
┡━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ kuiper   │ 23.95.242.52   │ ryan │ 22    │ id_rsa │ Never     │
│ 2   │ charon   │ 159.65.243.4   │ ryan │ 22    │ id_rsa │ Never     │
│ 3   │ callisto │ 192.168.50.96  │ ryan │ 3356  │ id_rsa │ Never     │
│ 4   │ firefly  │ 192.168.50.151 │ ryan │ 22    │ id_rsa │ Never     │
│ 5   │ hyperion │ 192.168.50.200 │ ryan │ 22    │ id_rsa │ Never     │
│ 6   │ pluto    │ 107.173.38.148 │ ryan │ 22    │ id_rsa │ Never     │
└─────┴──────────┴────────────────┴──────┴───────┴────────┴───────────┘

Total: 6 connections
```

## Security Fixes Applied (2026-03-22)

The following issues were identified and fixed during a code review session:

- **File permissions**: `connections.json`, `~/.ssh/config.tengingarstjori`, and the config directory are now created with `0o600`/`0o700` permissions using `os.open` atomically — no world-readable window.
- **SSH config injection**: Input fields (`name`, `host`, `identity_file`, `proxy_jump`, `extra_options`) are validated to reject newline characters; `notes` has newlines stripped. This prevents crafted values from injecting extra SSH config directives.
- **Error propagation**: Save and config-write failures now raise instead of printing silently, so the CLI no longer reports success when data was never persisted.
- **Built-in shadowing**: `ConnectionError` and `PermissionError` in `exceptions.py` renamed to `SSHConnectionError` and `SSHPermissionError` to avoid masking Python built-ins.
- **Correctness fixes**: `is_initialized()`, include-line detection, `fix_config` escape depth, `validate` command, and interactive port input all corrected.
