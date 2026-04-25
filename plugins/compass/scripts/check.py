#!/usr/bin/env python3
"""Entry point for /compass:check. Reads .compass.toml, computes Direction
Index, prints markdown briefing on stdout."""
from __future__ import annotations

import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib.runtime import collect_commits, load_repo_cfg, maybe_issues, reconfigure_utf8  # noqa
from lib.direction import compute  # noqa: E402
from lib.output import render_briefing  # noqa: E402


def main() -> int:
    reconfigure_utf8()
    loaded = load_repo_cfg(silent=False)
    assert loaded is not None  # silent=False raises SystemExit on failure
    repo, cfg = loaded
    commits = collect_commits(repo, cfg)
    result = compute(commits, cfg, maybe_issues(repo, cfg))
    sys.stdout.write(render_briefing(result, commits, cfg))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
