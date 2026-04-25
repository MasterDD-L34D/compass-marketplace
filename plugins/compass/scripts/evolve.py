#!/usr/bin/env python3
"""Entry point for /compass:evolve. Reads Claude Code transcripts of the
current project, aggregates stats (counts only — no content extracted),
and proposes config changes for user review. Never auto-applies."""
from __future__ import annotations

import sys
from pathlib import Path

_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
if str(_PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(_PLUGIN_ROOT))

from lib.runtime import load_repo_cfg, reconfigure_utf8  # noqa: E402
from lib.evolve import aggregate, find_transcript_dir, propose  # noqa: E402


def main() -> int:
    reconfigure_utf8()
    loaded = load_repo_cfg(silent=False)
    assert loaded is not None
    repo, cfg = loaded
    td = find_transcript_dir(repo)
    if td is None:
        sys.stdout.write(
            "# Compass — Evolve\n\n"
            "Nessuna directory `~/.claude/projects/<repo>` trovata.\n"
            "Compass evolve richiede transcript Claude Code per analizzare il pattern di uso.\n"
        )
        return 0
    pillar_ids = [p["id"] for p in cfg["pillars"]]
    stats = aggregate(td, pillar_ids)
    proposals = propose(stats, cfg)

    out: list[str] = ["# Compass — Evolve\n"]
    out.append(f"**Transcripts**: `{td.name}` · {stats.sessions} sessioni · "
               f"{stats.total_lines} eventi totali · "
               f"{stats.compass_mentions} menzioni `compass`\n")
    out.append("## Menzioni dei pilastri")
    if stats.pillar_mentions:
        for pid in pillar_ids:
            out.append(f"- `{pid}`: {stats.pillar_mentions.get(pid, 0)}")
    else:
        out.append("- (nessuna menzione registrata)")
    out.append("")
    out.append("## Proposte (nessuna applicata automaticamente)")
    for i, p in enumerate(proposals, 1):
        out.append(f"### {i}. {p.kind} → `{p.target}`")
        out.append(f"**Motivazione**: {p.reason}  ")
        out.append(f"**Azione suggerita**: {p.suggestion}")
        out.append("")
    out.append("> Nessuna modifica al `.compass.toml` viene applicata. Per accettare una "
               "proposta, modifica il file a mano o ri-esegui `/compass:init` (richiede "
               "rimozione del file esistente).")
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
