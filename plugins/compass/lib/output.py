"""Render briefings: full (/compass:check) and mini (/compass:boot, hook).
Spec: docs/config.md §9."""
from __future__ import annotations

from datetime import date
from typing import Any

from .direction import DirectionResult, drift_signals, next_smallest_step
from .classify import CommitHit


def _verdict(score: float, t: dict, with_emoji: bool = False) -> tuple[str, str]:
    if score >= t["healthy"]:
        return ("🟢", "rotta coerente") if with_emoji else ("", "rotta coerente")
    if score < t["warning"]:
        return ("🔴", "deriva evidente") if with_emoji else ("", "deriva evidente")
    return ("🟡", "attenzione") if with_emoji else ("", "attenzione")


def render_briefing(result: DirectionResult, commits: list[CommitHit],
                    cfg: dict[str, Any]) -> str:
    f = cfg["direction"]["formula"]
    _, verdict = _verdict(result.score, cfg["direction"]["thresholds"])
    issue_val = f"{result.issue_factor:.2f}" if result.issues_enabled else "n/d (off)"
    touched = sum(1 for n in result.pillars_touched.values() if n > 0)
    L = [
        "# Compass — Direction check\n",
        f"**Direction Index: {result.score:.0f} / 100** ({verdict}) · "
        f"window: {result.window} commits · generated: {date.today().isoformat()}\n",
        "## Breakdown\n",
        "| Componente       | Peso | Valore | Contributo |",
        "|------------------|-----:|-------:|-----------:|",
        f"| Core share       | {f['core_share']:.2f} | {result.core_share*100:5.0f}% | {result.core_contrib:>10.1f} |",
        f"| Pillar coverage  | {f['pillar_coverage']:.2f} |   {touched}/{result.pillars_total} | {result.pillar_contrib:>10.1f} |",
        f"| Issue factor     | {f['issue_factor']:.2f} | {issue_val:>6} | {result.issue_contrib:>10.1f} |",
        "",
        "## Pilastri nel window",
    ]
    if not result.pillars_touched:
        L.append("- (nessun pilastro dichiarato)")
    else:
        for p in cfg["pillars"]:
            n = result.pillars_touched.get(p["id"], 0)
            if n > 0:
                L.append(f"- [x] `{p['id']}` ({n} commit)")
            else:
                L.append(f"- [ ] **`{p['id']}`** ← 0 commit")
    L.append("")
    sigs = drift_signals(result, commits, cfg)
    L.append("## Drift signals (ranked)")
    if sigs:
        L.extend(f"{i}. {s}" for i, s in enumerate(sigs, 1))
    else:
        L.append("- Nessun segnale di deriva sopra la soglia. ✓")
    L.append("")
    step = next_smallest_step(result, cfg)
    L.append("## Next smallest step")
    L.append(step if step else "Nessuna correzione urgente. Continua.")
    return "\n".join(L).rstrip() + "\n"


def render_brief_mini(result: DirectionResult, commits: list[CommitHit],
                      cfg: dict[str, Any]) -> str:
    """3-5 line direction brief for /compass:boot and SessionStart hook."""
    emoji, verdict = _verdict(result.score, cfg["direction"]["thresholds"], with_emoji=True)
    touched = sum(1 for n in result.pillars_touched.values() if n > 0)
    lines = [f"{emoji} **Compass — DI {result.score:.0f}/100** ({verdict}) · "
             f"pilastri {touched}/{result.pillars_total} · window {result.window} commit"]
    sigs = drift_signals(result, commits, cfg)
    if sigs:
        lines.append(f"⚠ {sigs[0]}")
    step = next_smallest_step(result, cfg)
    if step:
        lines.append(f"→ {step}")
    return "\n".join(lines) + "\n"
