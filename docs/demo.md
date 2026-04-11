# Tengingarstjóri — SSH Connection Manager

*2026-04-11T00:32:30Z by Showboat 0.6.1*
<!-- showboat-id: 797902dc-7b16-457d-bbf4-7d47921d4d0a -->

Tengingarstjóri ("tg") is a non-invasive SSH connection manager. It stores connections in `~/.tengingarstjori/connections.json` and generates a separate `~/.ssh/config.tengingarstjori` file that is included into your main SSH config — leaving your existing setup completely untouched.

This document walks through every command with live output.

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
  clone         Clone an existing connection with a new name.
  config        Configure Tengingarstjóri settings.
  connect       Connect to an SSH server.
  export        Export connections for backup or sharing.
  fix-config    Fix corrupted SSH configuration.
  fix-forwards  Fix LocalForward and RemoteForward syntax in existing...
  history       Show recent connection history.
  import        Import connections from a JSON file.
  init          Initialize Tengingarstjóri and set up SSH config...
  list          List all SSH connections.
  refresh       Regenerate SSH configuration file.
  remove        Remove an SSH connection.
  reset         Reset SSH configuration to the original state before...
  show          Show detailed information about a connection.
  snippet       Show the SSH command or config block for a connection.
  test          Test SSH connection health.
  update        Update an existing SSH connection.
  validate      Validate SSH configuration syntax for all connections.
```

## Setup

Run `tg init` once to integrate with your SSH config. It creates a backup of your existing `~/.ssh/config` and adds a single `Include` line — all managed connections go into their own file.

```bash
tg init --help
```

```output
Usage: tg init [OPTIONS]

  Initialize Tengingarstjóri and set up SSH config integration.

Options:
  --help  Show this message and exit.
```

## Managing Connections

### Adding connections

Use `tg add` with flags for non-interactive use, or run it bare for a guided prompt. The `--non-interactive` flag requires all mandatory fields (`--name`, `--host`, `--user`) to be passed as flags.

```bash
tg add --help
```

```output
Usage: tg add [OPTIONS]

  Add a new SSH connection.

  Examples:     # Basic connections     tg add -n server1 -h 192.168.1.10 -u
  admin     tg add --name myserver --host example.com --user deploy --port
  2222

      # ProxyJump examples     tg add -n internal --host 10.0.1.100 -u admin
      --proxy-jump bastion.company.com     tg add -n db-server --host
      192.168.10.50 -u dbadmin --proxy-jump
      "jumpuser@bastion.company.com:2222"

      # Port forwarding examples (auto-corrected to proper SSH syntax)     tg
      add -n db-tunnel --host db.company.com -u dbuser --local-forward
      "3306:localhost:3306"     tg add -n dev-server --host dev.company.com -u
      dev --local-forward "8080:localhost:80,3306:db:3306"     tg add -n
      redis-tunnel --host redis.company.com -u admin --local-forward
      "6379:localhost:6379"

      # Complex example with multiple options     tg add -n prod-db --host
      prod-db.internal -u produser                --proxy-jump
      bastion.company.com                --local-forward "5432:localhost:5432"
      --key ~/.ssh/prod_key                --notes "Production database via
      bastion"

      tg add  # Interactive mode

Options:
  -n, --name TEXT        Connection name
  -h, --host TEXT        Host/IP address
  -u, --user TEXT        Username
  -p, --port INTEGER     SSH port (default: 22)
  --hostname TEXT        SSH HostName (if different from host)
  -k, --key TEXT         SSH private key path
  --proxy-jump TEXT      ProxyJump configuration
  --local-forward TEXT   LocalForward configuration
  --remote-forward TEXT  RemoteForward configuration
  --notes TEXT           Connection notes
  --non-interactive      Use non-interactive mode (requires all options via
                         flags)
  --help                 Show this message and exit.
```

The examples below use a demo environment pre-loaded with three connections:
- `prod-web` — a basic production server
- `bastion` — a jump host
- `staging-db` — a database server reached via ProxyJump with a local port forward

## tg add — Add a connection

Connections are added non-interactively with flags, or interactively with `tg add` (no flags). The port defaults to 22. ProxyJump and port forwarding syntax is auto-normalised.

```bash
HOME=/tmp/tg-demo-4zATs tg add --name bastion --host bastion.example.com --user jump --notes 'Jump host for internal network' --non-interactive
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ➕ Add SSH Connection                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
SSH config backed up to /tmp/tg-demo-4zATs/.ssh/config.backup
Added include line to /tmp/tg-demo-4zATs/.ssh/config
✓ Added connection 'bastion'
Connect with: ssh bastion
```

```bash
HOME=/tmp/tg-demo-4zATs tg add --name staging-db --host 10.0.2.20 --user dbadmin --port 5432 --proxy-jump bastion --local-forward '5432:localhost:5432' --notes 'Staging database via bastion' --non-interactive
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ➕ Add SSH Connection                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Added connection 'staging-db'
Connect with: ssh staging-db
```

## tg list — List connections

Lists all connections in a table. Use `--detailed` for full info, `--format json` for scripting.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list
```

```output
                                SSH Connections                                 
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ #   ┃ Name       ┃ Host              ┃ User    ┃ Port  ┃ Key     ┃ Last Used ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ prod-web   │ 10.0.1.10         │ deploy  │ 22    │ default │ Never     │
│ 2   │ bastion    │ bastion.example.… │ jump    │ 22    │ default │ Never     │
│ 3   │ staging-db │ 10.0.2.20         │ dbadmin │ 5432  │ default │ Never     │
└─────┴────────────┴───────────────────┴─────────┴───────┴─────────┴───────────┘

Total: 3 connections
```

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --detailed
```

```output
                           SSH Connections (Detailed)                           
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━┓
┃ #   ┃ Name       ┃ Connection    ┃ Advanced      ┃ Notes         ┃ Last Used ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ prod-web   │ deploy@10.0.… │ None          │ Production    │ Never     │
│     │            │               │               │ web server    │           │
├─────┼────────────┼───────────────┼───────────────┼───────────────┼───────────┤
│ 2   │ bastion    │ jump@bastion… │ None          │ Jump host for │ Never     │
│     │            │               │               │ internal      │           │
│     │            │               │               │ network       │           │
├─────┼────────────┼───────────────┼───────────────┼───────────────┼───────────┤
│ 3   │ staging-db │ dbadmin@10.0… │ ProxyJump:    │ Staging       │ Never     │
│     │            │               │ bastion       │ database via  │           │
│     │            │               │ LocalForward: │ bastion       │           │
│     │            │               │ 5432          │               │           │
│     │            │               │ localhost:54… │               │           │
└─────┴────────────┴───────────────┴───────────────┴───────────────┴───────────┘

Total: 3 connections
```

### Filtering and sorting

`tg list` supports tag filtering, full-text search, sorting, and an `--unused` filter.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --format json
```

```output
[
  {
    "id": "10b9ba65-d230-41ae-ab2c-3fc3122b61e8",
    "name": "prod-web",
    "host": "10.0.1.10",
    "user": "deploy",
    "port": 22
  },
  {
    "id": "48064f10-75d5-40fb-aa2f-93e206027870",
    "name": "bastion",
    "host": "bastion.example.com",
    "user": "jump",
    "port": 22
  },
  {
    "id": "78803b30-dfd8-4872-bfb5-f4338e129c55",
    "name": "staging-db",
    "host": "10.0.2.20",
    "user": "dbadmin",
    "port": 5432
  }
]
```

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --tag production
```

```output
                                SSH Connections                                
┏━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ #   ┃ Name     ┃ Host                ┃ User   ┃ Port  ┃ Key     ┃ Last Used ┃
┡━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ prod-web │ 10.0.1.10           │ deploy │ 22    │ default │ Never     │
│ 2   │ bastion  │ bastion.example.com │ jump   │ 22    │ default │ Never     │
└─────┴──────────┴─────────────────────┴────────┴───────┴─────────┴───────────┘

Total: 2 connections
```

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --search bastion
```

```output
                                SSH Connections                                 
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ #   ┃ Name       ┃ Host              ┃ User    ┃ Port  ┃ Key     ┃ Last Used ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ bastion    │ bastion.example.… │ jump    │ 22    │ default │ Never     │
│ 2   │ staging-db │ 10.0.2.20         │ dbadmin │ 5432  │ default │ Never     │
└─────┴────────────┴───────────────────┴─────────┴───────┴─────────┴───────────┘

Total: 2 connections
```

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --unused
```

```output
                                SSH Connections                                 
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┓
┃ #   ┃ Name       ┃ Host              ┃ User    ┃ Port  ┃ Key     ┃ Last Used ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━┩
│ 1   │ prod-web   │ 10.0.1.10         │ deploy  │ 22    │ default │ Never     │
│ 2   │ bastion    │ bastion.example.… │ jump    │ 22    │ default │ Never     │
│ 3   │ staging-db │ 10.0.2.20         │ dbadmin │ 5432  │ default │ Never     │
└─────┴────────────┴───────────────────┴─────────┴───────┴─────────┴───────────┘

Total: 3 connections
```

## tg show — Inspect a connection

Shows all fields for a single connection, including the generated SSH config block. Reference by name or list position number.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg show staging-db
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ 🔗 staging-db                                                                │
╰──────────────────────────────────────────────────────────────────────────────╯
┌─────────────────┬──────────────────────────────┐
│ Host            │ 10.0.2.20                    │
│ User            │ dbadmin                      │
│ Port            │ 5432                         │
│ ProxyJump       │ bastion                      │
│ LocalForward    │ 5432 localhost:5432          │
│ Notes           │ Staging database via bastion │
│ Created         │ 2026-04-10 20:33             │
│ Use Count       │ 0                            │
└─────────────────┴──────────────────────────────┘

SSH Config Block:
╭──────────────────────────────────────────────────────────────────────────────╮
│ Host staging-db                                                              │
│     # Staging database via bastion                                           │
│     HostName 10.0.2.20                                                       │
│     User dbadmin                                                             │
│     Port 5432                                                                │
│     ProxyJump bastion                                                        │
│     LocalForward 5432 localhost:5432                                         │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## tg connect — Connect to a server

Looks up the connection, updates `last_used` and `use_count`, then calls `ssh <name>`. Use `--dry-run` to preview the command without connecting.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg connect prod-web --dry-run
```

```output
ssh prod-web
```

Without `--dry-run`, `tg connect prod-web` would replace the current process with `ssh prod-web`.

## tg update — Modify a connection

Updates specific fields without touching others. In non-interactive mode, only the flags you pass are changed.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg update prod-web --host 10.0.1.20 --notes 'Production web server (new IP)' --non-interactive
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ✏️  Update SSH Connection                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Updated connection 'prod-web'
  host: 10.0.1.20
  notes: Production web server (new IP)
```

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg show prod-web
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ 🔗 prod-web                                                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
┌─────────────────┬────────────────────────────────┐
│ Host            │ 10.0.1.20                      │
│ User            │ deploy                         │
│ Port            │ 22                             │
│ Notes           │ Production web server (new IP) │
│ Created         │ 2026-04-10 20:33               │
│ Last Used       │ 2026-04-10 20:34               │
│ Use Count       │ 1                              │
└─────────────────┴────────────────────────────────┘

SSH Config Block:
╭──────────────────────────────────────────────────────────────────────────────╮
│ Host prod-web                                                                │
│     # Production web server (new IP)                                         │
│     HostName 10.0.1.20                                                       │
│     User deploy                                                              │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## tg clone — Duplicate a connection

Copies all settings to a new name, resetting usage stats. Useful for staging/production variants.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg clone prod-web prod-web-eu
```

```output
✓ Cloned 'prod-web' as 'prod-web-eu'
```

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg show prod-web-eu
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ 🔗 prod-web-eu                                                               │
╰──────────────────────────────────────────────────────────────────────────────╯
┌─────────────────┬────────────────────────────────┐
│ Host            │ 10.0.1.20                      │
│ User            │ deploy                         │
│ Port            │ 22                             │
│ Notes           │ Production web server (new IP) │
│ Created         │ 2026-04-10 20:34               │
│ Use Count       │ 0                              │
└─────────────────┴────────────────────────────────┘

SSH Config Block:
╭──────────────────────────────────────────────────────────────────────────────╮
│ Host prod-web-eu                                                             │
│     # Production web server (new IP)                                         │
│     HostName 10.0.1.20                                                       │
│     User deploy                                                              │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

## tg snippet — Get the SSH command or config block

Outputs a pipe-friendly SSH command or the raw SSH config block. Useful for scripts or copying to clipboard.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg snippet staging-db
```

```output
ssh -p 5432 -J bastion -L 5432 localhost:5432 dbadmin@10.0.2.20
```

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg snippet staging-db --config
```

```output
Host staging-db
    # Staging database via bastion
    HostName 10.0.2.20
    User dbadmin
    Port 5432
    ProxyJump bastion
    LocalForward 5432 localhost:5432

```

## tg history — Recent connection activity

Shows connections sorted by most-recently used. The `--dry-run` connect above counted as a use, so `prod-web` now appears in history.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg history
```

```output
                         Connection History                         
┏━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ #   ┃ Name     ┃ Last Used        ┃ Use Count ┃ Connection       ┃
┡━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 1   │ prod-web │ 2026-04-10 20:34 │         1 │ deploy@10.0.1.20 │
└─────┴──────────┴──────────────────┴───────────┴──────────────────┘
```

## tg export / tg import — Backup and restore

Export to JSON or raw SSH config format. Import with conflict resolution strategies: `skip` (default), `overwrite`, or `rename`.

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg export
```

```output
[
  {
    "id": "10b9ba65-d230-41ae-ab2c-3fc3122b61e8",
    "name": "prod-web",
    "host": "10.0.1.20",
    "hostname": null,
    "port": 22,
    "user": "deploy",
    "identity_file": null,
    "proxy_jump": null,
    "local_forward": null,
    "remote_forward": null,
    "extra_options": {},
    "notes": "Production web server (new IP)",
    "tags": [
      "production",
      "web"
    ],
    "created_at": "2026-04-10T20:33:35.154728",
    "last_used": "2026-04-10T20:34:43.560962",
    "use_count": 1
  },
  {
    "id": "48064f10-75d5-40fb-aa2f-93e206027870",
    "name": "bastion",
    "host": "bastion.example.com",
    "hostname": null,
    "port": 22,
    "user": "jump",
    "identity_file": null,
    "proxy_jump": null,
    "local_forward": null,
    "remote_forward": null,
    "extra_options": {},
    "notes": "Jump host for internal network",
    "tags": [
      "production",
      "infra"
    ],
    "created_at": "2026-04-10T20:33:35.303618",
    "last_used": null,
    "use_count": 0
  },
  {
    "id": "78803b30-dfd8-4872-bfb5-f4338e129c55",
    "name": "staging-db",
    "host": "10.0.2.20",
    "hostname": null,
    "port": 5432,
    "user": "dbadmin",
    "identity_file": null,
    "proxy_jump": "bastion",
    "local_forward": "5432 localhost:5432",
    "remote_forward": null,
    "extra_options": {},
    "notes": "Staging database via bastion",
    "tags": [],
    "created_at": "2026-04-10T20:33:35.448910",
    "last_used": null,
    "use_count": 0
  },
  {
    "id": "e07e00ce-1bdd-4f62-b7d5-58a8e4f57bf3",
    "name": "prod-web-eu",
    "host": "10.0.1.20",
    "hostname": null,
    "port": 22,
    "user": "deploy",
    "identity_file": null,
    "proxy_jump": null,
    "local_forward": null,
    "remote_forward": null,
    "extra_options": {},
    "notes": "Production web server (new IP)",
    "tags": [
      "production",
      "web"
    ],
    "created_at": "2026-04-10T20:34:52.645010",
    "last_used": null,
    "use_count": 0
  }
]
```

```bash
HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg export -f ssh-config
```

```output
Host prod-web
    # Production web server (new IP)
    HostName 10.0.1.20
    User deploy

Host bastion
    # Jump host for internal network
    HostName bastion.example.com
    User jump

Host staging-db
    # Staging database via bastion
    HostName 10.0.2.20
    User dbadmin
    Port 5432
    ProxyJump bastion
    LocalForward 5432 localhost:5432

Host prod-web-eu
    # Production web server (new IP)
    HostName 10.0.1.20
    User deploy


```

Exporting to a file for backup, then importing into a fresh environment with `--strategy rename` to show conflict handling:

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg export -o /tmp/tg-backup.json
```

```output
✓ Exported 4 connections to /tmp/tg-backup.json
```

```bash
env HOME=/tmp/tg-import-home tg import /tmp/tg-backup.json
```

```output
SSH config backed up to /tmp/tg-import-home/.ssh/config.backup
Added include line to /tmp/tg-import-home/.ssh/config

✓ Imported: 4, Skipped: 0, Errors: 0
```

Re-importing into an environment that already has these connections demonstrates the `skip` strategy (default):

```bash
env HOME=/tmp/tg-import-home tg import /tmp/tg-backup.json
```

```output
Skipped 'prod-web' (already exists)
Skipped 'bastion' (already exists)
Skipped 'staging-db' (already exists)
Skipped 'prod-web-eu' (already exists)

✓ Imported: 0, Skipped: 4, Errors: 0
```

Use `--strategy rename` to import without overwriting, auto-suffixing duplicates as `name-2`, `name-3`, etc.

## tg remove — Remove a connection

Prompts for confirmation unless `--force` is passed.

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg remove prod-web-eu --force
```

```output
✓ Removed connection 'prod-web-eu'
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list
```

```output
                                SSH Connections                                 
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ #   ┃ Name       ┃ Host             ┃ User    ┃ Port  ┃ Key     ┃ Last Used  ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ prod-web   │ 10.0.1.20        │ deploy  │ 22    │ default │ 2026-04-10 │
│ 2   │ bastion    │ bastion.example… │ jump    │ 22    │ default │ Never      │
│ 3   │ staging-db │ 10.0.2.20        │ dbadmin │ 5432  │ default │ Never      │
└─────┴────────────┴──────────────────┴─────────┴───────┴─────────┴────────────┘

Total: 3 connections
```

## tg validate — Check configuration integrity

Validates all connections: checks for spaces in names, missing identity files, and that SSH config blocks can be generated cleanly.

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg validate
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ 🔍 SSH Configuration Validation                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ prod-web: OK
✓ bastion: OK
✓ staging-db: OK

All configurations are valid!
```

## tg test — Check SSH connectivity

Attempts a real SSH connection (`BatchMode=yes`, no login shell). Reports OK, Failed, or Timeout. Use `--all` to check every connection.

```bash
tg test --help
```

```output
Usage: tg test [OPTIONS] [CONNECTION_REF]

  Test SSH connection health.

  Examples:
    tg test myserver           # Test single connection
    tg test --all              # Test all connections
    tg test myserver -t 10     # Custom timeout

Options:
  --all                  Test all connections
  -t, --timeout INTEGER  Connection timeout in seconds (default: 5)
  --help                 Show this message and exit.
```

## Maintenance commands

| Command | What it does |
|---------|-------------|
| `tg refresh` | Regenerate `~/.ssh/config.tengingarstjori` from the connection database |
| `tg fix-config` | Remove corrupted `Include` lines and re-add a clean one |
| `tg fix-forwards` | Auto-correct old-style port forwarding syntax (e.g. `3306:localhost:3306` → `3306 localhost:3306`) |
| `tg validate` | Check all connections for config issues |
| `tg reset` | Restore original SSH config from backup, removing the `Include` line |

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg refresh
```

```output
Regenerating SSH configuration...
✓ SSH configuration refreshed
Config file: 
/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly/.ssh/config.teng
ingarstjori
```

The generated `~/.ssh/config.tengingarstjori` file looks like this:

```bash
cat /var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly/.ssh/config.tengingarstjori
```

```output
# Tengingarstjori SSH Connections
# Generated on 2026-04-10T20:36:02.988522
# Do not edit manually - use 'tg' commands

Host prod-web
    # Production web server (new IP)
    HostName 10.0.1.20
    User deploy

Host bastion
    # Jump host for internal network
    HostName bastion.example.com
    User jump

Host staging-db
    # Staging database via bastion
    HostName 10.0.2.20
    User dbadmin
    Port 5432
    ProxyJump bastion
    LocalForward 5432 localhost:5432

```

And the main `~/.ssh/config` gets a single `Include` prepended:

```bash
cat /var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly/.ssh/config
```

```output
Include /var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly/.ssh/config.tengingarstjori

# existing ssh config
```

---

All command output above was produced by running `tg` live against a temporary demo environment. Use `showboat verify docs/demo.md` to confirm every block still produces matching output.
