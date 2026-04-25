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
    pillar_ids = [p["id"] for p in cfg["pillars"]]
    pillars_total = len(pillar_ids)
    sum_core = 0.0
    sum_abs = 0.0
    pillars_touched: dict[str, int] = {pid: 0 for pid in pillar_ids}
    category_counts: dict[str, int] = {}

    for ch in commits:
        verify_mult = 1.0 if ch.verified else 0.5
        commit_pillars: set[str] = set()
        for fh in ch.files:
            w = fh.weight * verify_mult
            sum_abs += abs(w)
            if fh.category.startswith("pillar:") or fh.category == "core":
                sum_core += w
            if fh.pillar_id is not None:
                commit_pillars.add(fh.pillar_id)
        for pid in commit_pillars:
            pillars_touched[pid] += 1
        if ch.dominant_category:
            category_counts[ch.dominant_category] = category_counts.get(ch.dominant_category, 0) + 1

    core_share = max(0.0, min(1.0, sum_core / sum_abs if sum_abs > 0 else 0.0))
    pillar_coverage = (sum(1 for pid in pillar_ids if pillars_touched[pid] > 0) / pillars_total) \
        if pillars_total else 0.0
    if issues is not None:
        total = issues["open"] + issues["closed"]
        issue_factor = issues["closed"] / total if total > 0 else 0.5
        issues_enabled = True
    else:
        issue_factor = 0.5
        issues_enabled = False

    f = cfg["direction"]["formula"]
    core_contrib = core_share * 100 * f["core_share"]
    pillar_contrib = pillar_coverage * 100 * f["pillar_coverage"]
    issue_contrib = issue_factor * 100 * f["issue_factor"]
    score = core_contrib + pillar_contrib + issue_contrib

    return DirectionResult(
        score=round(score, 1), core_share=core_share, core_contrib=round(core_contrib, 1),
        pillar_coverage=pillar_coverage, pillar_contrib=round(pillar_contrib, 1),
        issue_factor=issue_factor, issue_contrib=round(issue_contrib, 1),
        pillars_touched=pillars_touched, pillars_total=pillars_total,
        category_counts=category_counts, window=len(commits), issues_enabled=issues_enabled,
    )


def drift_signals(result: DirectionResult, commits: list[CommitHit],
                  cfg: dict[str, Any]) -> list[str]:
    """Top 3 drift signals (one-liners), ordered by impact on score."""
    f = cfg["direction"]["formula"]
    sigs: list[tuple[float, str]] = []
    n_commits = len(commits)
    for pid, n in result.pillars_touched.items():
        if n == 0:
            sigs.append((f["pillar_coverage"] * 100 / max(1, result.pillars_total),
                         f"`{pid}` non toccato in {result.window} commit"))
    infra_n = result.category_counts.get("infra", 0)
    if n_commits and infra_n / n_commits > 0.3:
        sigs.append((8.0, f"{round(infra_n/n_commits*100)}% commit dominanti `infra` (soglia <30%)"))
    if result.core_share < 0.2 and result.window >= 10:
        sigs.append(((0.4 - result.core_share) * 100 * f["core_share"],
                     f"`core_share` solo {round(result.core_share*100)}% in window"))
    p_idx = [i for i, ch in enumerate(commits) if any(fh.pillar_id for fh in ch.files)]
    if p_idx and p_idx[0] > result.window // 2:
        sigs.append((5.0, f"ultimo commit core a {p_idx[0]} commit fa"))
    ambig = sum(1 for ch in commits if not ch.verified)
    if ambig >= 3:
        sigs.append((3.0, f"{ambig} commit con messaggio in conflitto coi file toccati"))
    sigs.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in sigs[:3]]


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
