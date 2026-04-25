# compass

Direction-first audit lens for Claude Code projects.

> This is the plugin body. For the philosophy and roadmap, see the
> [marketplace README](../../README.md), [VISION.md](../../VISION.md)
> and [ROADMAP.md](../../ROADMAP.md) at the repository root.

## What it does

Compass measures how well recent work on your project serves its declared
**pillars** (3–5 things that matter most). It surfaces **drift** (work
happening outside the pillars) and proposes the smallest realignment step.

It composes with other audit plugins instead of duplicating them.

## Status

**Pre-alpha (v0.0.1).** Scaffolding only — no commands implemented yet.
See [ROADMAP.md](../../ROADMAP.md) for milestones.

## Components (target, not yet shipped)

- `commands/` — slash commands (`/compass init|check|boot|drift|evolve`)
- `agents/` — subagents for drift classification and evolve proposals
- `skills/` — auto-invoked lens skills
- `hooks/` — optional `SessionStart` brief injection

## Config file

Projects opt in by creating `.compass.yaml` at their root. See
`docs/config.md` (planned v0.1.0) for the schema.

## License

MIT. See [LICENSE](../../LICENSE).
