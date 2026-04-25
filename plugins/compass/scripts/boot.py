#!/usr/bin/env python3
"""Entry point for /compass:boot and SessionStart hook (--hook flag).
Outputs 3-5 line direction brief. Silent (exit 0) if not opted in
(no .compass.toml), boot.enabled=false in hook context, or escape env set."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib.runtime import collect_commits, load_repo_cfg, maybe_issues, reconfigure_utf8  # noqa
from lib.direction import compute  # noqa: E402
from lib.output import render_brief_mini  # noqa: E402


def _claude_md_hint(cfg: dict, repo: Path) -> str | None:
    if cfg["boot"].get("delegate_claude_md") and (repo / "CLAUDE.md").exists():
        return "💡 `claude-md-management` installato? Considera `/claude-md:audit`."
    return None


def main(argv: list[str]) -> int:
    reconfigure_utf8()
    is_hook = "--hook" in argv
    loaded = load_repo_cfg(silent=is_hook)
    if loaded is None:
        return 0
    repo, cfg = loaded
    boot = cfg["boot"]
    if is_hook:
        if not boot.get("enabled", True):
            return 0
        if os.environ.get(boot.get("escape_env", "COMPASS_SKIP_BOOT")):
            return 0
    commits = collect_commits(repo, cfg)
    result = compute(commits, cfg, maybe_issues(repo, cfg))
    sys.stdout.write(render_brief_mini(result, commits, cfg))
    hint = _claude_md_hint(cfg, repo)
    if hint:
        sys.stdout.write(hint + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
