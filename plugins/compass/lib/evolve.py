"""Read Claude Code transcripts + aggregate stats + propose config changes.
Spec: docs/config.md, ROADMAP v0.4.0. Privacy: only counts, no content extracted."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class EvolveStats:
    sessions: int = 0
    total_lines: int = 0
    compass_mentions: int = 0
    pillar_mentions: dict[str, int] = field(default_factory=dict)
    transcript_dir: Path | None = None


def find_transcript_dir(repo: Path) -> Path | None:
    """Locate ~/.claude/projects/<escaped-repo-path>/ directory."""
    base = Path(os.path.expanduser("~")) / ".claude" / "projects"
    if not base.exists():
        return None
    parts = str(repo).replace("\\", "/").replace(":", "").lstrip("/").split("/")
    for cand in ("-" + "-".join(parts), "C-" + "-".join(parts)):
        p = base / cand
        if p.exists():
            return p
    needle = parts[-1].lower() if parts else ""
    for child in base.iterdir():
        if child.is_dir() and needle and needle in child.name.lower():
            return child
    return None


def aggregate(transcript_dir: Path, pillar_ids: list[str], limit_files: int = 20) -> EvolveStats:
    """Count session files + lines + occurrences of pillar ids and 'compass' markers."""
    stats = EvolveStats(transcript_dir=transcript_dir)
    pillar_re = re.compile(r"\b(" + "|".join(map(re.escape, pillar_ids)) + r")\b") if pillar_ids else None
    files = sorted(transcript_dir.glob("*.jsonl"),
                   key=lambda p: p.stat().st_mtime, reverse=True)[:limit_files]
    stats.sessions = len(files)
    for f in files:
        try:
            with f.open(encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    stats.total_lines += 1
                    low = line.lower()
                    if "compass" in low:
                        stats.compass_mentions += 1
                    if pillar_re:
                        for m in pillar_re.finditer(line):
                            pid = m.group(1)
                            stats.pillar_mentions[pid] = stats.pillar_mentions.get(pid, 0) + 1
        except OSError:
            continue
    return stats


@dataclass
class Proposal:
    kind: str          # 'drop_pillar' | 'boost_weight' | 'add_paths_hint' | 'noop'
    target: str        # pillar id or section name
    reason: str
    suggestion: str    # human-readable action


def propose(stats: EvolveStats, cfg: dict[str, Any]) -> list[Proposal]:
    """Compute proposals from stats + current config. Conservative: zero or few suggestions."""
    out: list[Proposal] = []
    if stats.sessions < 3:
        out.append(Proposal("noop", "*",
                            f"Solo {stats.sessions} sessione/i registrate.",
                            "Continua a usare Compass; rieseguire `/compass:evolve` dopo 5+ sessioni."))
        return out
    pillars = {p["id"]: p for p in cfg["pillars"]}
    mentions = stats.pillar_mentions
    total_m = sum(mentions.values()) or 1
    avg = total_m / max(1, len(pillars))
    for pid, p in pillars.items():
        m = mentions.get(pid, 0)
        share = m / total_m
        if m == 0 and stats.sessions >= 5:
            out.append(Proposal("drop_pillar", pid,
                                f"`{pid}` non menzionato in {stats.sessions} sessioni.",
                                f"Considera rimuovere il pilastro `{pid}` da `.compass.toml`."))
        elif share > 0.5 and p.get("weight", 1.0) < 1.5 and len(pillars) > 1:
            out.append(Proposal("boost_weight", pid,
                                f"`{pid}` domina ({share*100:.0f}% delle menzioni).",
                                f"Considera alzare `weight` di `{pid}` "
                                f"da {p.get('weight', 1.0)} a {min(2.0, p.get('weight', 1.0) + 0.5)}."))
        elif m < avg * 0.3 and stats.sessions >= 5:
            out.append(Proposal("add_paths_hint", pid,
                                f"`{pid}` ha solo {m} menzioni vs media {avg:.1f}.",
                                f"Verifica i `paths` di `{pid}`: forse troppo restrittivi."))
    if not out:
        out.append(Proposal("noop", "*",
                            "Pattern di uso bilanciato sui pilastri dichiarati.",
                            "Nessuna modifica suggerita. Continua."))
    return out
