"""Render the /compass:check briefing markdown. Spec: docs/config.md §9."""
from __future__ import annotations

from datetime import date
from typing import Any

from .direction import DirectionResult, drift_signals, next_smallest_step
from .classify import CommitHit


def render_briefing(result: DirectionResult, commits: list[CommitHit],
                    cfg: dict[str, Any]) -> str:
    f = cfg["direction"]["formula"]
    t = cfg["direction"]["thresholds"]

    if result.score >= t["healthy"]:
        verdict = "rotta coerente"
    elif result.score < t["warning"]:
        verdict = "deriva evidente"
    else:
        verdict = "attenzione"

    issue_val = (f"{result.issue_factor:.2f}"
                 if result.issues_enabled else "n/d (off)")

    lines: list[str] = []
    lines.append("# Compass — Direction check\n")
    lines.append(
        f"**Direction Index: {result.score:.0f} / 100** "
        f"({verdict}) · window: {result.window} commits · "
        f"generated: {date.today().isoformat()}\n"
    )
    lines.append("## Breakdown\n")
    lines.append("| Componente       | Peso | Valore | Contributo |")
    lines.append("|------------------|-----:|-------:|-----------:|")
    lines.append(
        f"| Core share       | {f['core_share']:.2f} | "
        f"{result.core_share*100:5.0f}% | {result.core_contrib:>10.1f} |"
    )
    touched = sum(1 for n in result.pillars_touched.values() if n > 0)
    lines.append(
        f"| Pillar coverage  | {f['pillar_coverage']:.2f} | "
        f"  {touched}/{result.pillars_total} | {result.pillar_contrib:>10.1f} |"
    )
    lines.append(
        f"| Issue factor     | {f['issue_factor']:.2f} | "
        f"{issue_val:>6} | {result.issue_contrib:>10.1f} |"
    )
    lines.append("")

    lines.append("## Pilastri nel window")
    if not result.pillars_touched:
        lines.append("- (nessun pilastro dichiarato)")
    else:
        for p in cfg["pillars"]:
            pid = p["id"]
            n = result.pillars_touched.get(pid, 0)
            mark = "[x]" if n > 0 else "[ ]"
            label = f"`{pid}`" if n > 0 else f"**`{pid}`** ← 0 commit"
            suffix = f" ({n} commit)" if n > 0 else ""
            lines.append(f"- {mark} {label}{suffix}")
    lines.append("")

    signals = drift_signals(result, commits, cfg)
    lines.append("## Drift signals (ranked)")
    if not signals:
        lines.append("- Nessun segnale di deriva sopra la soglia. ✓")
    else:
        for i, s in enumerate(signals, 1):
            lines.append(f"{i}. {s}")
    lines.append("")

    step = next_smallest_step(result, cfg)
    lines.append("## Next smallest step")
    lines.append(step if step else "Nessuna correzione urgente. Continua.")
    return "\n".join(lines).rstrip() + "\n"
