"""Compute Direction Index from classified commits. Spec: docs/config.md §6, §9."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .classify import CommitHit


@dataclass
class DirectionResult:
    score: float
    core_share: float
    core_contrib: float
    pillar_coverage: float
    pillar_contrib: float
    issue_factor: float
    issue_contrib: float
    pillars_touched: dict[str, int]
    pillars_total: int
    category_counts: dict[str, int]
    window: int
    issues_enabled: bool


def compute(commits: list[CommitHit], cfg: dict[str, Any],
            issues: dict[str, int] | None) -> DirectionResult:
    pids = [p["id"] for p in cfg["pillars"]]
    pt: dict[str, int] = {pid: 0 for pid in pids}
    cc: dict[str, int] = {}
    sum_core = sum_abs = 0.0
    for ch in commits:
        m = 1.0 if ch.verified else 0.5
        seen: set[str] = set()
        for fh in ch.files:
            w = fh.weight * m
            sum_abs += abs(w)
            if fh.category.startswith("pillar:") or fh.category == "core":
                sum_core += w
            if fh.pillar_id:
                seen.add(fh.pillar_id)
        for pid in seen:
            pt[pid] += 1
        if ch.dominant_category:
            cc[ch.dominant_category] = cc.get(ch.dominant_category, 0) + 1
    core = max(0.0, min(1.0, sum_core / sum_abs if sum_abs > 0 else 0.0))
    cov = (sum(1 for pid in pids if pt[pid] > 0) / len(pids)) if pids else 0.0
    if issues is not None:
        tot = issues["open"] + issues["closed"]
        iss, iss_on = (issues["closed"] / tot if tot > 0 else 0.5), True
    else:
        iss, iss_on = 0.5, False
    f = cfg["direction"]["formula"]
    cc_, pc_, ic_ = core * 100 * f["core_share"], cov * 100 * f["pillar_coverage"], iss * 100 * f["issue_factor"]
    return DirectionResult(
        score=round(cc_ + pc_ + ic_, 1), core_share=core, core_contrib=round(cc_, 1),
        pillar_coverage=cov, pillar_contrib=round(pc_, 1),
        issue_factor=iss, issue_contrib=round(ic_, 1),
        pillars_touched=pt, pillars_total=len(pids),
        category_counts=cc, window=len(commits), issues_enabled=iss_on,
    )


def drift_signals(result: DirectionResult, commits: list[CommitHit],
                  cfg: dict[str, Any], top: int = 3) -> list[str]:
    """Drift signals (one-liners), ordered by impact. Default top 3."""
    f = cfg["direction"]["formula"]
    sigs: list[tuple[float, str]] = []
    n = len(commits)
    for pid, c in result.pillars_touched.items():
        if c == 0:
            sigs.append((f["pillar_coverage"] * 100 / max(1, result.pillars_total),
                         f"`{pid}` non toccato in {result.window} commit"))
    infra_n = result.category_counts.get("infra", 0)
    if n and infra_n / n > 0.3:
        sigs.append((8.0, f"{round(infra_n/n*100)}% commit dominanti `infra` (soglia <30%)"))
    if result.core_share < 0.2 and result.window >= 10:
        sigs.append(((0.4 - result.core_share) * 100 * f["core_share"],
                     f"`core_share` solo {round(result.core_share*100)}% in window"))
    p_idx = [i for i, ch in enumerate(commits) if any(fh.pillar_id for fh in ch.files)]
    if p_idx and p_idx[0] > result.window // 2:
        sigs.append((5.0, f"ultimo commit core a {p_idx[0]} commit fa"))
    ambig = sum(1 for ch in commits if not ch.verified)
    if ambig >= 3:
        sigs.append((3.0, f"{ambig} commit con messaggio in conflitto coi file toccati"))
    import time
    recency_d = cfg.get("drift", {}).get("recency_days", 7)
    last_core = next((ch for ch in commits if any(fh.pillar_id for fh in ch.files)), None)
    if commits and last_core is None and result.window >= 5:
        sigs.append((6.0, f"nessun commit core nel window ({result.window})"))
    elif last_core and last_core.ts:
        days = (int(time.time()) - last_core.ts) // 86400
        if days > recency_d:
            sigs.append((4.0, f"ultimo commit core {days} giorni fa (soglia drift {recency_d}gg)"))
    sigs.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in sigs[:top]]


def next_smallest_step(result: DirectionResult, cfg: dict[str, Any]) -> str | None:
    untouched = [pid for pid, n in result.pillars_touched.items() if n == 0]
    if untouched:
        for p in cfg["pillars"]:
            if p["id"] == untouched[0]:
                hint = (p.get("paths") or ["(no paths declared)"])[0]
                return f"Apri un commit su `{untouched[0]}`. Path più promettente: `{hint}`."
    if result.core_share < 0.3 and result.window >= 5:
        return "Prossimo commit: tocca un file dentro un pilastro dichiarato."
    return None
