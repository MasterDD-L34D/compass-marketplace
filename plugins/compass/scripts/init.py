#!/usr/bin/env python3
"""Helpers for /compass:init. Subcommands: inspect | write <toml-file>.
The interactive Q&A is driven by Claude reading inspect output;
this script is a pure utility."""
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PLUGIN_ROOT = _HERE.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib import config as cfgmod  # noqa: E402
from lib import git as gitmod     # noqa: E402

PROJECT_TYPE_BY_SIGNALS: list[tuple[str, list[str]]] = [
    ("multi-agent", ["agents/", "camel-agents/", "crewai/", "autogen/",
                     "SWARM-PILLARS.md", "MEMORY-SHARED.md", "cycle-log.md",
                     "requirements.txt:crewai", "requirements.txt:autogen",
                     "pyproject.toml:camel", "package.json:autogen"]),
    ("game-dev", ["assets", "scenes", "godot.project", "Game.uproject", "ProjectSettings/",
                  "package.json:phaser", "Cargo.toml:bevy"]),
    ("web-saas", ["next.config.js", "next.config.ts", "remix.config.js",
                  "package.json:next", "package.json:remix"]),
    ("library",  ["pyproject.toml", "setup.py", "Cargo.toml", "package.json:main", "go.mod"]),
    ("research", ["notebooks/", "*.ipynb", "data/raw/", "experiments/"]),
    ("docs",     ["mkdocs.yml", "docusaurus.config.js", "_config.yml", "book.toml"]),
]

# Pillars whose paths don't match anything in repo are dropped at suggest time.
DEFAULT_PILLAR_TEMPLATES: dict[str, list[tuple[str, str, list[str]]]] = {
    "game-dev": [("gameplay-core", "Gameplay & feel", ["src/game/**", "scenes/**", "assets/**"]),
                 ("balance-data", "Balance & data", ["data/**", "balance/**"]),
                 ("tactics-readability", "Lettura tattica UI", ["ui/**", "hud/**"])],
    "web-saas": [("core-funnel", "Core funnel", ["app/(main)/**", "src/pages/**"]),
                 ("perf-reliability", "Performance & reliability", ["src/lib/**", "src/server/**"]),
                 ("onboarding", "Onboarding", ["src/onboarding/**", "app/(onboarding)/**"])],
    "library":  [("api-stability", "API stability", ["src/**", "lib/**"]),
                 ("examples", "Examples & docs", ["examples/**", "docs/**"]),
                 ("compat-perf", "Compatibility & perf", ["benches/**", "tests/perf/**"])],
    "research": [("experiments", "Experiments", ["experiments/**", "notebooks/**"]),
                 ("writeup", "Writeup & figures", ["paper/**", "figures/**"]),
                 ("reproducibility", "Reproducibility", ["env/**", "scripts/**"])],
    "docs":     [("content", "Content", ["docs/**", "src/**"]),
                 ("navigation", "Navigation & IA", ["mkdocs.yml", "_config.yml", "sidebars.*"])],
    "multi-agent": [
        ("agent-identity", "Identity & profiles", ["agents/**/IDENTITY*", "MANIFEST.md"]),
        ("orchestration", "Coordination & handoffs", ["**/orchestrator*", "**/swarm_loop*", "contracts/**"]),
        ("shared-memory", "Memory & lessons", ["MEMORY-SHARED*", "logs/**", "cycle-log*"]),
    ],
    "other":    [("core", "Core", ["src/**"])],
}


def _signal_match(repo: Path, sig: str) -> bool:
    try:
        if ":" in sig:
            f, n = sig.split(":", 1); p = repo / f
            return p.exists() and n in p.read_text(encoding="utf-8", errors="ignore")
        if "*" in sig or "?" in sig: return bool(list(repo.glob(sig)))
        if sig.endswith("/"): return (repo / sig.rstrip("/")).is_dir()
        return (repo / sig).exists()
    except OSError:
        return False


def _detect_project_type(repo: Path) -> str:
    for ptype, signals in PROJECT_TYPE_BY_SIGNALS:
        if any(_signal_match(repo, s) for s in signals):
            return ptype
    return "other"


def _top_dirs(repo: Path) -> list[str]:
    skip = {".git", "node_modules", "__pycache__", "dist", "build", ".venv", "venv"}
    return [c.name for c in sorted(repo.iterdir())
            if c.is_dir() and c.name not in skip and not c.name.startswith(".")]


def _suggest_pillars(repo: Path, ptype: str) -> list[dict]:
    template = DEFAULT_PILLAR_TEMPLATES.get(ptype, DEFAULT_PILLAR_TEMPLATES["other"])
    suggested: list[dict] = []
    for pid, name, paths in template:
        kept = [p for p in paths if _has_match(repo, p)]
        if kept:
            suggested.append({"id": pid, "name": name, "paths": kept})
    if not suggested:
        dirs = _top_dirs(repo)
        if dirs:
            suggested.append({"id": "core", "name": "Core", "paths": [f"{dirs[0]}/**"]})
    return suggested


def _has_match(repo: Path, pattern: str) -> bool:
    try:
        return any(True for _ in repo.glob(pattern.replace("**", "*")))
    except (OSError, ValueError):
        return False


def cmd_inspect(repo_arg: str | None) -> int:
    cwd = Path.cwd() if repo_arg is None else Path(repo_arg).resolve()
    try:
        repo = gitmod.repo_root(cwd)
    except gitmod.GitError as e:
        print(json.dumps({"error": str(e)})); return 2
    ptype = _detect_project_type(repo)
    print(json.dumps({
        "repo_root": str(repo), "name": repo.name, "project_type": ptype,
        "top_dirs": _top_dirs(repo),
        "has_readme": any((repo / n).exists() for n in ("README.md", "readme.md", "README.rst")),
        "has_existing_config": (repo / ".compass.toml").exists(),
        "suggested_pillars": _suggest_pillars(repo, ptype),
    }, indent=2, ensure_ascii=False))
    return 0


def cmd_write(toml_file: str) -> int:
    src = Path(toml_file).resolve()
    if not src.exists():
        print(f"ERROR: file not found: {src}", file=sys.stderr); return 2
    try:
        with src.open("rb") as f:
            tomllib.load(f)
        cfg = cfgmod.load(src)
        repo = gitmod.repo_root(Path.cwd())
    except tomllib.TOMLDecodeError as e:
        print(f"ERROR: invalid TOML: {e}", file=sys.stderr); return 3
    except cfgmod.ConfigError as e:
        print(f"ERROR: schema validation failed: {e}", file=sys.stderr); return 4
    except gitmod.GitError as e:
        print(f"ERROR: {e}", file=sys.stderr); return 5
    dst = repo / ".compass.toml"
    if dst.exists():
        print(f"ERROR: {dst} already exists. Remove it first to re-init.", file=sys.stderr)
        return 6
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"OK: wrote {dst} (pillars: {len(cfg['pillars'])})")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "inspect":
        return cmd_inspect(argv[1] if len(argv) > 1 else None)
    if len(argv) >= 2 and argv[0] == "write":
        return cmd_write(argv[1])
    print("usage: init.py inspect [REPO] | write TOMLFILE", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
