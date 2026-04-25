---
name: init
description: Interactively create .compass.toml for the current project. Inspects the repo, proposes 3-5 pillars based on detected project type, asks the user to confirm/edit each, then writes the file. Use when the user asks "init compass", "set up compass", "create compass config", "compass init", "/compass:init".
allowed-tools: Bash, Read, Write
---

# /compass:init — interactive setup

Goal: guide the user through creating a valid `.compass.toml` at the
repo root. Schema spec: `docs/config.md`.

## Step 1 — Inspect the repo

Run the inspector to get a structured view:

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/init.py" inspect
```

The output is JSON with:

- `repo_root`, `name`, `project_type` (auto-detected: game-dev, web-saas,
  research, library, docs, or other)
- `top_dirs` — top-level directories
- `has_existing_config` — if true, **stop and tell the user** they
  already have one. Don't overwrite without consent.
- `suggested_pillars` — list of `{id, name, paths}` proposals filtered
  against actual repo paths

## Step 2 — Confirm with the user

Present the inspector summary in plain language. Then walk through the
suggested pillars **one at a time**, asking the user:

> Pillar 1/3: `<id>` — `<name>`
> Paths: `<paths>`
>
> Keep, edit, rename, or skip? (k/e/r/s)

For each:
- **k**: keep as-is
- **e**: ask for revised paths (one per line)
- **r**: ask for new id + name
- **s**: drop the pillar

After the proposed list, ask if they want to **add** a pillar that
wasn't suggested. Cap total at 10. Require at least 1.

If `project_type` was detected wrong, ask the user to override before
walking pillars. The 6 valid types: game-dev, web-saas, research,
library, docs, other.

## Step 3 — Write the file

Build the final TOML in memory using this exact structure (one
`[[pillars]]` block per pillar, no extras beyond what was confirmed):

```toml
version = 1

[project]
name = "<repo name>"
type = "<one of the 6 valid types>"

[[pillars]]
id = "<kebab-case>"
name = "<human label>"
description = "<optional, can be empty>"
paths = ["<glob>", "..."]
weight = 1.0
```

Show the user the final TOML and ask for one last confirm. On yes,
write it via the helper (which validates and refuses to overwrite an
existing `.compass.toml`):

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/init.py" write /tmp/compass-proposed.toml
```

Where `/tmp/compass-proposed.toml` is the file you wrote with the
agreed content. Use `Write` to create it before the shell call.

## Step 4 — Next step

After OK, suggest running `/compass:check` to see the first Direction
Index. Don't run it automatically.

## Constraints

- Never overwrite an existing `.compass.toml`. Ask the user to remove
  it manually first.
- Never invent paths the user didn't confirm.
- Stay within the schema in `docs/config.md`. Don't add fields the
  validator will reject.
- Keep the dialogue short: one question at a time, no walls of text.
