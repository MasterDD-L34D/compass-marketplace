#!/usr/bin/env python3
"""Entry point for /compass:check. Reads .compass.toml, computes Direction Index,
prints markdown briefing on stdout. Exits non-zero on config errors."""
from __future__ import annotations

import sys
from pathlib import Path

# Force UTF-8 on stdout/stderr (Windows defaults to cp1252).
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            pass

# Allow running from anywhere: add plugin root to sys.path so `lib.*` resolves.
_HERE = Path(__file__).resolve().parent
_PLUGIN_ROOT = _HERE.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib import config as cfgmod  # noqa: E402
from lib import git as gitmod     # noqa: E402
from lib.classify import classify_commit  # noqa: E402
from lib.direction import compute  # noqa: E402
from lib.output import render_briefing  # noqa: E402


def main(argv: list[str]) -> int:
    cwd = Path.cwd()
    try:
        repo = gitmod.repo_root(cwd)
    except gitmod.GitError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    cfg_path = cfgmod.find_config(repo)
    if cfg_path is None:
        print(
            "ERROR: no .compass.toml found in repo. Run /compass:init first.",
            file=sys.stderr,
        )
        return 3

    try:
        cfg = cfgmod.load(cfg_path)
    except cfgmod.ConfigError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 4

    window = cfg["direction"]["window"]
    try:
        commits_raw = gitmod.recent_commits(repo, window)
    except gitmod.GitError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 5

    commits = [classify_commit(c, cfg) for c in commits_raw]

    issues = None
    if cfg["issues"]["enabled"]:
        issues = gitmod.issues_summary(repo, cfg["issues"]["closed_window_days"])

    result = compute(commits, cfg, issues)
    sys.stdout.write(render_briefing(result, commits, cfg))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
