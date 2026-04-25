# CLAUDE.md — Working file for compass-marketplace

> Questo file è letto da Claude Code all'inizio di ogni sessione su questo
> repo. Contiene le regole non-negoziabili del progetto. **Leggilo prima di
> ogni task.**

---

## Cos'è questo repo

`compass-marketplace` è un Claude Code **plugin marketplace**. Pubblica un
unico plugin: `compass`, che aggiunge una **lente direzionale** (Pillars,
Direction Index, Drift detection) ai progetti Claude Code.

Origine filosofica: tool di monitoring di
[Evo-Tactics](https://github.com/MasterDD-L34D/Game), trasposto da
gaming a universale.

## Fonti di verità

Prima di pianificare qualunque task, **leggi**:

1. `VISION.md` — perché Compass esiste, i 3 primitivi, cosa NON farà
2. `ROADMAP.md` — milestone con scope e definition of done
3. `README.md` — pitch e ecosistema (chi delega a chi)

Se un task contraddice questi tre file, il task è sbagliato. Fermati e
chiedi all'utente.

## Stack & comandi

- **Linguaggio**: Python 3.11+ (stdlib only — niente pip install).
  Il bump a 3.11 è richiesto per `tomllib` (parser TOML stdlib, usato per
  `.compass.toml`). Vedi `docs/config.md` §7.
- **Formato**: Claude Code plugin spec (vedi `.claude-plugin/`)
- **Test**: `pytest` se introdotto, `python3 -m unittest` come fallback
- **Lint**: nessun linter forzato. Se serve: `ruff check` (opzionale)

```bash
# Validazione manifest
python3 -m json.tool .claude-plugin/marketplace.json
python3 -m json.tool plugins/compass/.claude-plugin/plugin.json

# Test plugin localmente (richiede Claude Code installato)
/plugin marketplace add .            # da dentro Claude Code, dalla root del repo
/plugin install compass@compass-marketplace
```

## Architettura — i 3 primitivi

1. **Pillars** — file `.compass.toml` nella root del progetto utente, dichiara
   3–5 cose che contano. Schema in `docs/config.md` (da scrivere v0.1.0).
2. **Direction Index** — numero 0–100. Pesato su % commit Core, copertura
   pilastri, issue chiuse.
3. **Drift** — segnali concreti che il lavoro recente non serve i pilastri.

Tutto il resto è UI sopra questi tre.

## Vincoli non-negoziabili

- 🚫 **No scope creep.** Ogni feature deve passare il test "questo è lente o
  è sistema?". Se è sistema → fuori.
- 🚫 **No rewrite di tool esistenti.** Vedi `README.md#ecosistema`. Se serve
  un audit di CLAUDE.md, **deleghi** a `claude-md-management`. Se serve un
  health check 360°, **deleghi** a `claude-doctor-skill`. Mai duplicare.
- 🚫 **No dipendenze pip.** Solo Python stdlib. Eccezioni vanno discusse
  prima.
- 🚫 **No background daemon / LLM agent.** Il ciclo evolutivo è
  pattern-matching su transcript, niente di più.
- 🚫 **No applicazione automatica di modifiche alla config utente.**
  `evolve` PROPONE, l'utente APPROVA.

## Budget di codice

| Componente | LOC max | Nota |
|---|---|---|
| Plugin Compass totale (Python) | 1000 | scaglione: 800 v0.1.0, 1000 da v0.3.0 |
| Singolo subagent | 100 righe | nel file `.md` |
| Singolo skill | 150 righe | nel `SKILL.md` |
| Singolo command | 80 righe | nel file `.md` |

Oltre questi numeri = stai aggiungendo sistema. Fermati.

**Storia del budget**: v0.1.0 fissava 800 LOC come design budget per
"lente non sistema". v0.3.0 ha bumped a 1000 per coprire `/compass:drift`
+ classificazione body keywords + recency drift signals. Ulteriori bump
richiedono giustificazione per milestone in commit message.

## Definition of done per ogni feature

1. Manifest `plugin.json` aggiornato con eventuali nuovi components
2. Documentazione: nuovo comando documentato in `plugins/compass/README.md`
3. Test manuale documentato: cosa hai testato e su quale repo
4. Commit conventional (`feat:`, `fix:`, `docs:`, `chore:`)
5. `ROADMAP.md` aggiornato spuntando il check completato
6. Validazione: `python3 -m json.tool` su tutti i JSON modificati

## Convenzioni di commit

```
feat(scope): aggiungi X
fix(scope): correggi Y
docs(scope): aggiorna doc Z
chore: housekeeping vario
refactor(scope): ristruttura W senza cambiare comportamento
```

Scope tipici: `init`, `check`, `boot`, `drift`, `evolve`, `marketplace`,
`docs`.

## Quando chiedere all'utente

Chiedi sempre prima di:
- Aggiungere una dipendenza esterna
- Modificare lo schema di `.compass.toml`
- Creare un nuovo command top-level
- Modificare README/VISION/ROADMAP (sono fonti di verità)
- Pushare su `main` (preferisci branch + chiedi review)

Decidi tu (senza chiedere) per:
- Refactor interni di moduli che hai scritto
- Aggiunta di test
- Fix di bug ovvi
- Aggiornamento di `.gitignore`
- Aggiunta di docstring / commenti

## Anti-pattern da evitare

| Anti-pattern | Perché è male |
|---|---|
| `pip install rich/click/typer` | Stdlib basta. Aumenta friction installazione. |
| Aggiungere "Phase 2/3/4..." a un command | Significa che il command sta diventando sistema. |
| File markdown >400 righe | Spezza in più file con index. |
| Riferimento a "AI generated" o "magic" | Sii preciso su cosa fa il codice. |
| Generare config "intelligenti" senza chiedere | `init` è interattivo, sempre. |
| Commit "WIP" o "stuff" su main | Branch + PR. |

## Quando una sessione si apre

1. Leggi questo file.
2. Leggi `ROADMAP.md` — qual è la milestone corrente?
3. Leggi gli ultimi 5 commit (`git log --oneline -5`).
4. Chiedi all'utente cosa vuole fare in questa sessione, **non** assumere.
