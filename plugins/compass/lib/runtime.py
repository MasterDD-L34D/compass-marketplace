"""Common entry-point helpers shared by check.py and boot.py."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from . import config as cfgmod
from . import git as gitmod
from .classify import classify_commit


def reconfigure_utf8() -> None:
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass


def _fail(msg: str, code: int, silent: bool) -> None:
    if silent:
        return None  # caller checks for None
    print(f"ERROR: {msg}", file=sys.stderr); raise SystemExit(code)


def load_repo_cfg(silent: bool = False) -> tuple[Path, dict[str, Any]] | None:
    """Resolve repo + load .compass.toml. silent=True → None on errors;
    silent=False → print + SystemExit."""
    try:
        repo = gitmod.repo_root(Path.cwd())
    except gitmod.GitError as e:
        return _fail(str(e), 2, silent)
    cfg_path = cfgmod.find_config(repo)
    if cfg_path is None:
        return _fail("no .compass.toml found in repo. Run /compass:init first.", 3, silent)
    try:
        return repo, cfgmod.load(cfg_path)
    except cfgmod.ConfigError as e:
        return _fail(str(e), 4, silent)


def collect_commits(repo: Path, cfg: dict[str, Any]) -> list:
    raws = gitmod.recent_commits(repo, cfg["direction"]["window"])
    return [classify_commit(c, cfg) for c in raws]


def maybe_issues(repo: Path, cfg: dict[str, Any]) -> dict | None:
    if not cfg["issues"]["enabled"]:
        return None
    return gitmod.issues_summary(repo, cfg["issues"]["closed_window_days"])
