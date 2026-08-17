# SKILL.md

This file teaches AI agents how to use `phabfive`, a CLI for Phabricator/Phorge. Focus is on common agent workflows: reading, searching, creating, and editing objects programmatically.

## Prerequisites

```bash
uv tool install phabfive
phabfive user setup                          # interactive wizard (URL + token → ~/.arcrc)
```

Or configure via environment variables:
```bash
export PHAB_URL=https://phorge.example.com/api/
export PHAB_TOKEN=cli-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Key Concepts

| Concept | Detail |
|---------|--------|
| **Monograms** | `T123` → `maniphest show T123`, `P123` → `paste show P123`, `K123` → `passphrase show K123`, `R123` → `diffusion branch list R123` |
| **Machine output** | `--format=json` or `--format=yaml` for programmatic consumption |
| **Monogram + text** | `phabfive T123 "comment text"` → `maniphest comment T123 "comment text"` |
| **Batch operations** | Comma-separated IDs: `phabfive edit T1,T2,T3 --status=resolved` |
| **Piped batch editing** | `phabfive maniphest search --assigned=@me \| phabfive edit --column=Done` |
| **Relative time filters** | Suffixes: `h`, `d`, `w`, `m`, `y` (e.g., `--updated-after=7d`, `--created-before=3m`) |

## Machine-Readable Output

Always use `--format=json` (preferred) or `--format=yaml` when the agent needs to parse output:

```bash
# Get a single task
phabfive --format=json T123

# Pipe to jq for field extraction
phabfive --format=json T123 | jq '.Task.Title'
phabfive --format=json T123 | jq -r '.Task.Description'
phabfive --format=json T123 | jq '.Task.Status'

# Search with structured output
phabfive --format=json maniphest search --tag=backend
phabfive --format=json maniphest search --assigned=@me
```

**Output field names** are capitalized (e.g., `Name`, `Status`, `Priority`, `Description`, `Assignee`, `Space`, `Boards`).

## Common Workflows

### 1. Read / Inspect Tasks

```bash
# Quick lookup (rich terminal output)
phabfive T123

# With full context
phabfive T123 --show-history --show-comments

# Machine-readable for parsing
phabfive --format=json T123 --show-history
phabfive --format=json T123 --show-comments
```

### 2. Search Tasks

```bash
# By text query
phabfive --format=json maniphest search "bug"
phabfive --format=json maniphest search --limit=50

# By project tag
phabfive --format=json maniphest search --tag=myproject
phabfive --format=json maniphest search --tag="Sprint 12"

# By assignee
phabfive --format=json maniphest search --assigned=@me

# Combined filters
phabfive --format=json maniphest search "performance" --tag=backend --assigned=@me

# Time-based
phabfive --format=json maniphest search --created-after=7d
phabfive --format=json maniphest search --updated-after=2w

# Status / priority filters
phabfive --format=json maniphest search --status=open
phabfive --format=json maniphest search --priority=unbreak

# Transition-based filters (for workflow analysis)
phabfive --format=json maniphest search --column=to:Done         # moved to Done
phabfive --format=json maniphest search --priority=raised         # priority was raised
phabfive --format=json maniphest search --status=backward         # status regressed
phabfive --format=json maniphest search --column=from:Backlog:forward  # moved from Backlog forward
```

### 3. Show Relationships

```bash
phabfive T123                        # shows Parents and Subtasks sections
phabfive maniphest parents T123      # just parent tasks
phabfive maniphest subtasks T123     # just subtasks
```

### 4. Create Tasks

```bash
# Simple create (opens $EDITOR for description)
phabfive maniphest create "Implement login"

# Inline description
phabfive maniphest create "Fix bug" --description="The login form crashes when..."

# With all fields
phabfive maniphest create "Refactor auth" \
  --description="Replace old auth middleware" \
  --priority=high \
  --status=open \
  --tag=backend \
  --assign=@me \
  --tag=Sprint12

# Create from stdin
echo "Multi-line\ndescription" | phabfive maniphest create "Task" --description=-
```

### 5. Edit Tasks

```bash
# Change status
phabfive edit T123 --status=resolved

# Change priority (by name or relative)
phabfive edit T123 --priority=high
phabfive edit T123 --priority=raise       # raise one level
phabfive edit T123 --priority=lower       # lower one level

# Move on board
phabfive edit T123 --tag=MyBoard --column=forward   # move forward
phabfive edit T123 --tag=MyBoard --column=Done      # move to specific column

# Edit title
phabfive edit T123 "New title"

# Add comment
phabfive edit T123 --comment="Fixed in commit abc123"

# Change assignee
phabfive edit T123 --assign=username

# Set parent tasks
phabfive edit T123 --parents=T456,T789            # set parents
phabfive edit T123 --parents=T456,T789 --force    # skip confirmation
phabfive edit T123 --depends-on=T456,T789         # set subtasks
phabfive maniphest create "Task" --depends-on=T456  # create with subtask

# Add tags / subscribers
phabfive edit T123 --tag=backend
phabfive edit T123 --subscribe=username

# Batch edit multiple tasks
phabfive edit T1,T2,T3 --status=resolved --comment="All fixed"

# Pipe search results into batch edit
phabfive maniphest search --assigned=@me | phabfive edit --column=Done
```

### 6. Work with Pastes

```bash
# Show paste
phabfive --format=json P123
phabfive P123                                 # with content

# Create paste
phabfive paste create "Config" --content="key=value"
phabfive paste create "Script" script.py     # from file
echo "content" | phabfive paste create "Stdin" --content=-

# Search pastes
phabfive --format=json paste search "config"
phabfive --format=json paste search --author=@me --limit=20
```

### 7. Work with Passphrase Credentials

```bash
# Show credential
phabfive --format=json K1

# Get just the secret value (for piping)
phabfive passphrase show K1 --format=simple | pbcopy
phabfive passphrase show K1 --format=simple | gh secret set MY_SECRET

# Search credentials
phabfive --format=json passphrase search         # all credentials
phabfive --format=json passphrase search --type=ssh
phabfive --format=json passphrase search "deploy" --show-secret
```

### 8. Diffusion (Repository Info)

```bash
# List repositories
phabfive --format=json diffusion repo list
phabfive --format=json diffusion repo list --url

# List branches
phabfive diffusion branch list R123

# List URIs (clone URLs)
phabfive --format=json diffusion uri list R123 --clone
```

### 9. User Info

```bash
phabfive user whoami       # show current user for all configured hosts
```

## Common jq Patterns

```bash
# Extract task titles from search results
phabfive --format=json maniphest search --tag=backend | jq -r '.[].Task.Name'

# Get task IDs and titles
phabfive --format=json maniphest search --assigned=@me | jq -r '.[] | "\(.Task.ID): \(.Task.Name)"'

# Get description
phabfive --format=json T123 | jq -r '.Task.Description'

# Get all comments as plain text
phabfive --format=json T123 --show-comments | jq -r '.Comments[] | "\(.Author): \(.Content)"'

# Filter tasks by status
phabfive --format=json maniphest search --tag=backend | jq '.[] | select(.Task.Status == "Open")'

# Get credential values
phabfive --format=json passphrase search --type=ssh | jq -r '.[].Secret'
```

## Safety Guidance

- **NEVER** run create/edit/delete operations on production unless you are explicitly asked to.
- The local test instance (`PHAB_URL=http://phorge.domain.tld/api/` with `PHAB_TOKEN=api-supersecr3tapikeyfordevelop1`) is safe for data-altering operations.
- Use `--dry-run` to preview changes: `phabfive --dry-run edit T123 --status=resolved`.
- Override `--dry-run` with `--execute`/`--no-dry-run` if needed.

## Output Formats Summary

| Format | Use case |
|--------|----------|
| `rich` (default TTY) | Human-readable terminal output |
| `json` | **Best for AI agents** — easy to parse with `jq` |
| `yaml` | Machine-readable alternative |
| `simple` | Minimal output (just the secret or content) |
| `tree` | Visual tree with link as root |

When stdout is piped or redirected, the default format falls back to yaml (or to the value of `PHAB_FALLBACK` if set to `json`).
