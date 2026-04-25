# compass

Direction-first audit lens for Claude Code projects.

> Plugin body. For philosophy and roadmap, see the
> [marketplace README](../../README.md), [VISION.md](../../VISION.md)
> and [ROADMAP.md](../../ROADMAP.md) at the repository root.

## What it does

Compass measures how well recent work serves your project's declared
**pillars** (3–5 things that matter most). It surfaces **drift** (work
happening outside the pillars) and proposes the smallest realignment
step.

Composes with other audit plugins instead of duplicating them.

## Status

**v0.2.0 — "Boot"**. Three slash commands + SessionStart hook:

- `/compass:init` — interactive setup of `.compass.toml`
- `/compass:check` — full Direction Index briefing
- `/compass:boot` — 3-line mini-brief for kickoff
- `SessionStart` hook — auto mini-brief on session open (opt-out via
  `boot.enabled = false` or `COMPASS_SKIP_BOOT=1`)

Plus auto-invoked skill `/compass:lens` for "am I on track" queries.

## Commands

### `/compass:init`

Inspects the repo (top-level dirs, README, project type signals),
proposes 3–5 pillars based on detected project type, walks you through
confirming/editing each one, then writes `.compass.toml` at the repo
root. Refuses to overwrite an existing config.

Runs `scripts/init.py inspect` to gather data, then `scripts/init.py
write` to commit the validated TOML.

### `/compass:check`

Reads `.compass.toml`, classifies the last N commits per category
(Core/Tests/Docs/Infra/Tooling/Other) using the path globs declared in
your pillars, computes the **Direction Index** with the formula in
[VISION.md §1](../../VISION.md), and prints a ≤40-line markdown briefing:

- DI score and verdict (rotta coerente / attenzione / deriva)
- Decomposed breakdown table (3 components, weighted contributions)
- Pillar checklist (touched / untouched in window)
- Top 3 drift signals (ranked by impact)
- Single next-smallest-step suggestion

Runs `scripts/check.py`.

### `/compass:boot`

Direction-aware kickoff. Same data as `/compass:check`, condensed to
3-5 lines:

```
🟢 Compass — DI 88/100 (rotta coerente) · pilastri 3/3 · window 30 commit
⚠ <top drift signal, if any>
→ <next smallest step, if applicable>
```

Wired to a `SessionStart` hook (`hooks/hooks.json`) that runs the same
brief automatically on session open. The hook is silent (exit 0, no
output) when:

- the project hasn't opted in (no `.compass.toml`)
- `boot.enabled = false` in config
- `COMPASS_SKIP_BOOT` (or whatever `boot.escape_env` names) is set

If `boot.delegate_claude_md = true` and `CLAUDE.md` exists, the brief
includes a one-line hint suggesting `/claude-md:audit` (delegation,
not duplication — see `claude-md-management` plugin).

### `/compass:lens` (auto-invoked skill)

Triggered by phrases like "am I on track", "where am I going", "check
the project" — runs `/compass:check` and presents the briefing
verbatim.

## Components

- `skills/compass-init/SKILL.md` — `/compass:init`
- `skills/compass-check/SKILL.md` — `/compass:check`
- `skills/compass-boot/SKILL.md` — `/compass:boot`
- `skills/compass-lens/SKILL.md` — auto-invoked lens
- `scripts/{check,boot,init}.py` — Python entry points called from
  skills via shell injection (`${CLAUDE_PLUGIN_ROOT}/scripts/...`)
- `hooks/hooks.json` — `SessionStart` hook → `boot.py --hook`
- `lib/` — config parser, classifier, git reader, direction calculator,
  briefing renderer, runtime helpers
- `agents/` — empty, reserved for v0.4.0+

## Config file

Projects opt in by creating `.compass.toml` at their root. See
[`docs/config.md`](../../docs/config.md) for the full schema (TOML 1.0,
parsed by `tomllib` from Python stdlib ≥ 3.11).

Minimal valid config:

```toml
version = 1

[[pillars]]
id = "core"
name = "Core product"
paths = ["src/**"]
```

## Requirements

- Python ≥ 3.11 (for `tomllib`)
- `git` CLI in `PATH`
- `gh` CLI optional (for `[issues] enabled = true`); without it,
  issue_factor neutralizes to 0.5

## License

MIT. See [LICENSE](../../LICENSE).
