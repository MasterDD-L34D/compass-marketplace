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

**v0.1.0 — MVP "Pillars & Direction"**. Two slash commands shipped:

- `/compass:init` — interactive setup of `.compass.toml`
- `/compass:check` — Direction Index + pillar coverage + drift signals

Plus an auto-invoked skill `/compass:lens` that runs `check` when the
user asks "where am I going" / "am I on track" / "sono sulla strada
giusta".

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

### `/compass:lens` (auto-invoked skill)

Triggered by phrases like "am I on track", "where am I going", "check
the project" — runs `/compass:check` and presents the briefing
verbatim.

## Components

- `skills/compass-init/SKILL.md` — `/compass:init`
- `skills/compass-check/SKILL.md` — `/compass:check`
- `skills/compass-lens/SKILL.md` — auto-invoked lens
- `scripts/check.py`, `scripts/init.py` — Python entry points called
  from skills via shell injection
- `lib/` — internal modules (config parser, classifier, git reader,
  direction calculator, briefing renderer)
- `agents/`, `hooks/` — empty, reserved for v0.2.0+

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
