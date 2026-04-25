---
name: boot
description: Direction-aware kickoff for the start of a session. Prints a 3-5 line mini-brief (Direction Index + top drift + next-smallest-step) to orient the user fast. Use when the user says "boot", "kickoff", "compass boot", "start the session", "where do I start today".
allowed-tools: Bash
---

# /compass:boot — kickoff direzionale

Mini version of `/compass:check`: same data, three lines instead of
forty. Useful at session start to orient without burning context.

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/boot.py"
```

Present output verbatim. If the script prints nothing (silent exit), the
project is not Compass-opted-in (no `.compass.toml`) — suggest
`/compass:init` and stop. Don't add interpretation.

## Escape hatch

If user says "skip boot" or sets `COMPASS_SKIP_BOOT=1`, the
`SessionStart` hook stays silent. `/compass:boot` invoked directly
ignores the env var (manual call = explicit intent).

## When to delegate

If `boot.delegate_claude_md = true` in `.compass.toml` and the user has
`claude-md-management` installed, the brief includes a one-line hint
suggesting `/claude-md:audit`. Don't auto-run it; user decides.
