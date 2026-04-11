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


## Connection Commands

### tg add — Add a connection

Connections are added with flags (`--non-interactive`) or interactively (bare `tg add`).

```bash
tg add --help
```

```output
Usage: tg add [OPTIONS]

  Add a new SSH connection.

  Basic connections:
    tg add -n server1 -h 192.168.1.10 -u admin
    tg add --name myserver --host example.com --user deploy --port 2222

  ProxyJump:
    tg add -n internal --host 10.0.1.100 -u admin --proxy-jump bastion.company.com
    tg add -n db-server --host 192.168.10.50 -u dbadmin --proxy-jump "jumpuser@bastion.company.com:2222"

  Port forwarding (auto-corrected to proper SSH syntax):
    tg add -n db-tunnel --host db.company.com -u dbuser --local-forward "3306:localhost:3306"
    tg add -n dev-server --host dev.company.com -u dev --local-forward "8080:localhost:80,3306:db:3306"
    tg add -n redis-tunnel --host redis.company.com -u admin --local-forward "6379:localhost:6379"

  Complex example with multiple options:
    tg add -n prod-db --host prod-db.internal -u produser \
           --proxy-jump bastion.company.com \
           --local-forward "5432:localhost:5432" \
           --key ~/.ssh/prod_key \
           --notes "Production database via bastion"

  Interactive mode:
    tg add

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

Adding three connections — a basic server, a bastion jump host, and a database server that tunnels through it:

```bash
env HOME=/tmp/tg-add-demo tg add   --name prod-web --host 10.0.1.10 --user deploy   --notes 'Production web server' --non-interactive
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ➕ Add SSH Connection                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
SSH config backed up to /tmp/tg-add-demo/.ssh/config.backup
Added include line to /tmp/tg-add-demo/.ssh/config
✓ Added connection 'prod-web'
Connect with: ssh prod-web
```

```bash
env HOME=/tmp/tg-add-demo tg add   --name bastion --host bastion.example.com --user jump   --notes 'Jump host for internal network' --non-interactive
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ➕ Add SSH Connection                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Added connection 'bastion'
Connect with: ssh bastion
```

```bash
env HOME=/tmp/tg-add-demo tg add   --name staging-db --host 10.0.2.20 --user dbadmin --port 5432   --proxy-jump bastion --local-forward '5432:localhost:5432'   --notes 'Staging database via bastion' --non-interactive
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ➕ Add SSH Connection                                                        │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Added connection 'staging-db'
Connect with: ssh staging-db
```

### tg list — List connections

Standard table, detailed view, multiple output formats, and filtering.

```bash
tg list --help
```

```output
Usage: tg list [OPTIONS]

  List all SSH connections.

  Basic usage:
    tg list                    # Basic list
    tg list --detailed         # Show all details
    tg list -d                 # Short form for detailed

  Format options:
    tg list -f compact         # Compact format
    tg list -d -f compact      # Detailed compact format
    tg list -f json            # JSON output
    tg list -d -f json         # Detailed JSON output

  Filter and sort:
    tg list --tag production   # Filter by tag
    tg list -s webserver       # Search name, host, user, notes
    tg list --sort last-used   # Sort by last used
    tg list --unused           # Show only unused connections
    tg list -t prod -s web     # Combine filters

Options:
  -d, --detailed                  Show detailed information including notes,
                                  proxy settings, and port forwarding
  -f, --format [table|compact|json]
                                  Output format: table (default), compact, or
                                  json
  -t, --tag TEXT                  Filter by tag
  -s, --search TEXT               Search across name, host, user, and notes
  --sort [name|last-used|created|use-count]
                                  Sort connections
  --unused                        Show only unused connections
  --help                          Show this message and exit.
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

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --detailed
```

```output
                           SSH Connections (Detailed)                           
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ #   ┃ Name       ┃ Connection    ┃ Advanced     ┃ Notes         ┃ Last Used  ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ prod-web   │ deploy@10.0.… │ None         │ Production    │ 2026-04-10 │
│     │            │               │              │ web server    │            │
│     │            │               │              │ (new IP)      │            │
├─────┼────────────┼───────────────┼──────────────┼───────────────┼────────────┤
│ 2   │ bastion    │ jump@bastion… │ None         │ Jump host for │ Never      │
│     │            │               │              │ internal      │            │
│     │            │               │              │ network       │            │
├─────┼────────────┼───────────────┼──────────────┼───────────────┼────────────┤
│ 3   │ staging-db │ dbadmin@10.0… │ ProxyJump:   │ Staging       │ Never      │
│     │            │               │ bastion      │ database via  │            │
│     │            │               │ LocalForwar… │ bastion       │            │
│     │            │               │ 5432         │               │            │
│     │            │               │ localhost:5… │               │            │
└─────┴────────────┴───────────────┴──────────────┴───────────────┴────────────┘

Total: 3 connections
```

Filtering by tag, searching, and showing only unused connections:

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --tag production
```

```output
                                SSH Connections                                 
┏━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ #   ┃ Name     ┃ Host                ┃ User   ┃ Port  ┃ Key     ┃ Last Used  ┃
┡━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ prod-web │ 10.0.1.20           │ deploy │ 22    │ default │ 2026-04-10 │
│ 2   │ bastion  │ bastion.example.com │ jump   │ 22    │ default │ Never      │
└─────┴──────────┴─────────────────────┴────────┴───────┴─────────┴────────────┘

Total: 2 connections
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --search bastion
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
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --unused
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
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg list --sort last-used --format json
```

```output
[
  {
    "id": "10b9ba65-d230-41ae-ab2c-3fc3122b61e8",
    "name": "prod-web",
    "host": "10.0.1.20",
    "user": "deploy",
    "port": 22,
    "tags": [
      "production",
      "web"
    ]
  },
  {
    "id": "48064f10-75d5-40fb-aa2f-93e206027870",
    "name": "bastion",
    "host": "bastion.example.com",
    "user": "jump",
    "port": 22,
    "tags": [
      "production",
      "infra"
    ]
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

### tg show — Inspect a connection

Shows all fields and the generated SSH config block. Reference by name or list number.

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg show staging-db
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

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg show staging-db --format json
```

```output
{
  "id": "78803b30-dfd8-4872-bfb5-f4338e129c55",
  "name": "staging-db",
  "host": "10.0.2.20",
  "user": "dbadmin",
  "port": 5432,
  "proxy_jump": "bastion",
  "local_forward": "5432 localhost:5432",
  "notes": "Staging database via bastion",
  "created_at": "2026-04-10T20:33:35.448910",
  "last_used": null,
  "use_count": 0
}
```

### tg update — Modify a connection

Only the flags you pass are changed. In interactive mode a field-selection menu is shown.

```bash
tg update --help
```

```output
Usage: tg update [OPTIONS] CONNECTION_REF

  Update an existing SSH connection.

  Non-interactive examples:
    tg update myserver --host 192.168.1.100 --non-interactive
    tg update myserver --host 10.0.1.50 --port 2222 --user admin --non-interactive
    tg update 1 --host newhost.com --non-interactive

  Update connection name:
    tg update old-name --name new-name --non-interactive

  Update port forwarding:
    tg update db-server --local-forward "3306:localhost:3306" --non-interactive
    tg update app-server --local-forward "8080:localhost:80,3000:localhost:3000" --non-interactive

  Update tags:
    tg update prod-web --tags "production,web,critical" --non-interactive

  Interactive mode (field selection menu):
    tg update myserver
    tg update 1

  Notes:
    - Connection can be referenced by name or number (from 'tg list')
    - In non-interactive mode, only specified fields are updated
    - In interactive mode, you select which fields to update from a menu
    - Name updates are allowed but must not conflict with existing connections
    - All updates trigger SSH config file regeneration

Options:
  -n, --name TEXT        New connection name
  -h, --host TEXT        New host/IP address
  -u, --user TEXT        New username
  -p, --port INTEGER     New SSH port
  --hostname TEXT        New SSH HostName
  -k, --key TEXT         New SSH private key path
  --proxy-jump TEXT      New ProxyJump configuration
  --local-forward TEXT   New LocalForward configuration
  --remote-forward TEXT  New RemoteForward configuration
  --notes TEXT           New connection notes
  --tags TEXT            New tags (comma-separated)
  --non-interactive      Use non-interactive mode (update only specified
                         fields)
  --help                 Show this message and exit.
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg update bastion   --host 10.0.0.1 --notes 'Jump host (new IP)' --non-interactive
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ ✏️  Update SSH Connection                                                    │
╰──────────────────────────────────────────────────────────────────────────────╯
✓ Updated connection 'bastion'
  host: 10.0.0.1
  notes: Jump host (new IP)
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg show bastion
```

```output
╭──────────────────────────────────────────────────────────────────────────────╮
│ 🔗 bastion                                                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
┌─────────────────┬────────────────────┐
│ Host            │ 10.0.0.1           │
│ User            │ jump               │
│ Port            │ 22                 │
│ Notes           │ Jump host (new IP) │
│ Created         │ 2026-04-10 20:33   │
│ Use Count       │ 0                  │
└─────────────────┴────────────────────┘

SSH Config Block:
╭──────────────────────────────────────────────────────────────────────────────╮
│ Host bastion                                                                 │
│     # Jump host (new IP)                                                     │
│     HostName 10.0.0.1                                                        │
│     User jump                                                                │
│                                                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
```

### tg clone — Duplicate a connection

Copies all settings to a new name, resetting `use_count` and `last_used`. Handy for spinning up staging variants of production configs.

```bash
tg clone --help
```

```output
Usage: tg clone [OPTIONS] SOURCE_REF NEW_NAME

  Clone an existing connection with a new name.

  Examples:
    tg clone prod-web staging-web
    tg clone 1 prod-web-2

Options:
  --help  Show this message and exit.
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg clone prod-web prod-web-eu
```

```output
✓ Cloned 'prod-web' as 'prod-web-eu'
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg show prod-web-eu
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
│ Created         │ 2026-04-11 02:54               │
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

### tg remove — Remove a connection

Prompts for confirmation unless `--force` is passed. Accepts name or list number.

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
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ #   ┃ Name       ┃ Host      ┃ User    ┃ Port  ┃ Key     ┃ Last Used  ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ prod-web   │ 10.0.1.20 │ deploy  │ 22    │ default │ 2026-04-10 │
│ 2   │ bastion    │ 10.0.0.1  │ jump    │ 22    │ default │ Never      │
│ 3   │ staging-db │ 10.0.2.20 │ dbadmin │ 5432  │ default │ Never      │
└─────┴────────────┴───────────┴─────────┴───────┴─────────┴────────────┘

Total: 3 connections
```

## Workflow Commands

### tg connect — Connect to a server

Looks up the connection, increments `use_count`, records `last_used`, then calls `ssh <name>` via `execvp` (replacing the current process). Use `--dry-run` to preview without connecting.

```bash
tg connect --help
```

```output
Usage: tg connect [OPTIONS] CONNECTION_REF

  Connect to an SSH server.

  Examples:
    tg connect myserver          # Connect by name
    tg connect 1                 # Connect by number
    tg connect myserver --dry-run  # Show SSH command without connecting

Options:
  --dry-run  Print the SSH command without executing
  --help     Show this message and exit.
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg connect prod-web --dry-run
```

```output
ssh prod-web
```

Usage tracking is updated even on `--dry-run`:

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg show prod-web --format json
```

```output
{
  "id": "10b9ba65-d230-41ae-ab2c-3fc3122b61e8",
  "name": "prod-web",
  "host": "10.0.1.20",
  "user": "deploy",
  "port": 22,
  "notes": "Production web server (new IP)",
  "tags": [
    "production",
    "web"
  ],
  "created_at": "2026-04-10T20:33:35.154728",
  "last_used": "2026-04-11T02:54:11.981329",
  "use_count": 2
}
```

### tg history — Recent connection activity

Shows connections sorted by most-recently used.

```bash
tg history --help
```

```output
Usage: tg history [OPTIONS]

  Show recent connection history.

  Examples:
    tg history              # Last 10 connections
    tg history --all        # Full history
    tg history -n 5         # Last 5 connections

Options:
  --all                Show full history
  -n, --limit INTEGER  Number of recent connections to show (default: 10)
  --help               Show this message and exit.
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg history
```

```output
                         Connection History                         
┏━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ #   ┃ Name     ┃ Last Used        ┃ Use Count ┃ Connection       ┃
┡━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 1   │ prod-web │ 2026-04-11 02:54 │         2 │ deploy@10.0.1.20 │
└─────┴──────────┴──────────────────┴───────────┴──────────────────┘
```

### tg snippet — Get the SSH command or config block

Outputs a pipe-friendly SSH command or the raw SSH config block.

```bash
tg snippet --help
```

```output
Usage: tg snippet [OPTIONS] CONNECTION_REF

  Show the SSH command or config block for a connection.

  Examples:
    tg snippet myserver            # SSH command
    tg snippet myserver --config   # SSH config block
    tg snippet myserver | pbcopy   # Copy to clipboard (macOS)

Options:
  --config  Show SSH config block instead of command
  --help    Show this message and exit.
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg snippet staging-db
```

```output
ssh -p 5432 -J bastion -L 5432 localhost:5432 dbadmin@10.0.2.20
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg snippet staging-db --config
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

### tg test — Check SSH connectivity

Attempts a real SSH handshake using `BatchMode=yes` (no password prompt, no login shell). Reports OK, Failed, or Timeout per connection.

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

### tg export / tg import — Backup and restore

Export to JSON (default) or raw SSH config format. Import supports three conflict strategies: `skip` (default), `overwrite`, and `rename`.

```bash
tg export --help
```

```output
Usage: tg export [OPTIONS]

  Export connections for backup or sharing.

  Examples:
    tg export                          # JSON to stdout
    tg export -o backup.json           # JSON to file
    tg export -f ssh-config            # SSH config format to stdout
    tg export --strip-keys -o safe.json  # Export without key paths

Options:
  -o, --output TEXT               Output file path (default: stdout)
  -f, --format [json|ssh-config]  Export format
  --strip-keys                    Omit SSH key paths from export
  --help                          Show this message and exit.
```

```bash
tg import --help
```

```output
Usage: tg import [OPTIONS] FILEPATH

  Import connections from a JSON file.

  Examples:
    tg import backup.json                    # Skip existing
    tg import backup.json --strategy overwrite  # Overwrite conflicts
    tg import backup.json --strategy rename     # Rename conflicts

Options:
  --strategy [skip|overwrite|rename]
                                  Conflict resolution: skip (default),
                                  overwrite, or rename
  --help                          Show this message and exit.
```

```bash
env HOME=/var/folders/8b/9kdx1knj7msdw_c1v9d4_8tw0000gn/T/tmp.LMlzVVr1Ly tg export -f ssh-config
```

```output
Host prod-web
    # Production web server (new IP)
    HostName 10.0.1.20
    User deploy

Host bastion
    # Jump host (new IP)
    HostName 10.0.0.1
    User jump

Host staging-db
    # Staging database via bastion
    HostName 10.0.2.20
    User dbadmin
    Port 5432
    ProxyJump bastion
    LocalForward 5432 localhost:5432


```

```bash
env HOME=/tmp/tg-import-demo2 tg import /tmp/tg-backup.json
```

```output
SSH config backed up to /tmp/tg-import-demo2/.ssh/config.backup
Added include line to /tmp/tg-import-demo2/.ssh/config

✓ Imported: 3, Skipped: 0, Errors: 0
```

```bash
env HOME=/tmp/tg-import-demo2 tg list
```

```output
                             SSH Connections                             
┏━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ #   ┃ Name       ┃ Host      ┃ User    ┃ Port  ┃ Key     ┃ Last Used  ┃
┡━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ prod-web   │ 10.0.1.20 │ deploy  │ 22    │ default │ 2026-04-11 │
│ 2   │ bastion    │ 10.0.0.1  │ jump    │ 22    │ default │ Never      │
│ 3   │ staging-db │ 10.0.2.20 │ dbadmin │ 5432  │ default │ Never      │
└─────┴────────────┴───────────┴─────────┴───────┴─────────┴────────────┘

Total: 3 connections
```

Running import again with the default `skip` strategy leaves existing connections untouched:

```bash
env HOME=/tmp/tg-import-demo2 tg import /tmp/tg-backup.json
```

```output
Skipped 'prod-web' (already exists)
Skipped 'bastion' (already exists)
Skipped 'staging-db' (already exists)

✓ Imported: 0, Skipped: 3, Errors: 0
```

Use `--strategy rename` to import and auto-suffix conflicting names:

```bash
env HOME=/tmp/tg-import-demo2 tg import /tmp/tg-backup.json --strategy rename
```

```output
Renamed 'prod-web' to 'prod-web-2'
Renamed 'bastion' to 'bastion-2'
Renamed 'staging-db' to 'staging-db-2'

✓ Imported: 3, Skipped: 0, Errors: 0
```

```bash
env HOME=/tmp/tg-import-demo2 tg list
```

```output
                              SSH Connections                              
┏━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ #   ┃ Name         ┃ Host      ┃ User    ┃ Port  ┃ Key     ┃ Last Used  ┃
┡━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1   │ prod-web     │ 10.0.1.20 │ deploy  │ 22    │ default │ 2026-04-11 │
│ 2   │ bastion      │ 10.0.0.1  │ jump    │ 22    │ default │ Never      │
│ 3   │ staging-db   │ 10.0.2.20 │ dbadmin │ 5432  │ default │ Never      │
│ 4   │ prod-web-2   │ 10.0.1.20 │ deploy  │ 22    │ default │ 2026-04-11 │
│ 5   │ bastion-2    │ 10.0.0.1  │ jump    │ 22    │ default │ Never      │
│ 6   │ staging-db-2 │ 10.0.2.20 │ dbadmin │ 5432  │ default │ Never      │
└─────┴──────────────┴───────────┴─────────┴───────┴─────────┴────────────┘

Total: 6 connections
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
