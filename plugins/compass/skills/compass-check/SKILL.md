---
name: check
description: Compute the project's Direction Index (0-100) and surface drift. Reads .compass.toml from the repo root and analyzes the last N commits. Use when the user asks "where am I going", "am I on track", "check the project", "direction check", "compass check".
allowed-tools: Bash
---

Run the check script and present its output verbatim. The script reads
`.compass.toml` at the repo root, classifies the last N commits per
category (Core/Tests/Docs/Infra/Tooling/Other), and prints a markdown
briefing with the Direction Index, breakdown table, pillar coverage, top
drift signals, and the smallest next step.

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check.py"
```

After the script output, do not summarize or rephrase. The briefing is
the deliverable. If the script exits non-zero (no `.compass.toml`,
malformed schema, not a git repo), surface the exact error and suggest
running `/compass:init` first if the file is missing.
