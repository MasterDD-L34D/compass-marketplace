---
name: evolve
description: Analyze Claude Code transcripts of the current project and propose config changes (pillar drops, weight bumps, path widenings) based on actual usage. Never auto-applies. Use when the user says "evolve compass", "improve config", "tune compass", "adatta compass", "compass evolve", "make compass better".
allowed-tools: Bash
---

# /compass:evolve — proposte da pattern di uso

Analizza i transcript Claude Code del progetto corrente
(`~/.claude/projects/<repo>/*.jsonl`) e propone modifiche al
`.compass.toml`. **Mai applica** automaticamente — l'utente decide.

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/evolve.py"
```

Presenta l'output verbatim. Le proposte sono di 4 tipi:

- `drop_pillar`: pilastro mai menzionato → suggerisci rimozione
- `boost_weight`: pilastro dominante (>50% menzioni) → suggerisci alzare il peso
- `add_paths_hint`: pilastro sotto-menzionato → suggerisci verificare i path
- `noop`: nessuna modifica utile rilevata

**Privacy**: Il parser conta solo occorrenze (line counts, mention counts).
Nessun contenuto dei transcript viene estratto, citato o esposto.

## Dopo le proposte

Se l'utente vuole accettare una proposta:

1. **Drop pillar**: chiedi conferma, poi rimuovi a mano la sezione
   `[[pillars]]` corrispondente da `.compass.toml`. Per re-init pulito,
   rimuovi `.compass.toml` e ri-esegui `/compass:init`.
2. **Boost weight**: edit chirurgico al campo `weight` del pilastro.
3. **Add paths**: chiedi all'utente quali path aggiungere; edit a mano.

Auto-apply (con TOML writer + diff) è rinviato a v0.5.0+.

## Soglie attuali

- `sessions < 3`: nessuna proposta (dati insufficienti)
- `mentions == 0` && `sessions >= 5`: drop_pillar
- `share > 50%` && `weight < 1.5`: boost_weight
- `mentions < 30% media` && `sessions >= 5`: add_paths_hint
