#!/usr/bin/env python3
"""Entry point for /compass:drift. Focused drift report."""
from __future__ import annotations

import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib.runtime import collect_commits, load_repo_cfg, maybe_issues, reconfigure_utf8  # noqa
from lib.direction import compute, drift_signals, next_smallest_step  # noqa: E402


def main() -> int:
    reconfigure_utf8()
    loaded = load_repo_cfg(silent=False)
    assert loaded is not None
    repo, cfg = loaded
    commits = collect_commits(repo, cfg)
    result = compute(commits, cfg, maybe_issues(repo, cfg))
    th = cfg["drift"]["warning_threshold"]
    sigs = drift_signals(result, commits, cfg, top=5)
    step = next_smallest_step(result, cfg)
    head = (f"⚠ **DRIFT WARNING** · DI {result.score:.0f} < soglia {th}"
            if result.score < th else
            f"✓ DI {result.score:.0f} ≥ soglia {th}: nessun warning attivo.")
    body = ("\n".join(f"{i}. {s}" for i, s in enumerate(sigs, 1))
            if sigs else "- Nessun segnale di deriva sopra soglia.")
    sys.stdout.write(
        f"# Compass — Drift report\n\n{head}\n\n## Segnali rilevati\n{body}\n\n"
        f"## Prossimo passo di riallineamento\n"
        f"{step or 'Nessuna correzione urgente. Continua.'}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
