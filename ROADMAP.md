# Roadmap

> _Dove stiamo andando. Piano incrementale, non vincolante._

Il principio ogni volta: **se non serve ancora, non costruirlo.**

---

## v0.0.1 — "Piantare la bandiera" ✅ (siamo qui)

**Scope:** marketplace e plugin scaffolding vuoto ma valido.

- [x] Struttura directory conforme a Claude Code plugin spec
- [x] `marketplace.json` valido
- [x] `plugin.json` valido
- [x] `README.md` — pitch del marketplace
- [x] `VISION.md` — manifesto filosofico
- [x] `ROADMAP.md` (questo file)
- [x] `LICENSE` (MIT)
- [x] `.gitignore`

**Criterio di done:** il marketplace può essere aggiunto con
`/plugin marketplace add` e il plugin può essere "installato" senza errori
(anche se non fa nulla).

**Stima:** ~2 ore di lavoro. Fatto.

---

## v0.1.0 — MVP "Pillars & Direction"

**Scope:** due comandi che dimostrano la lente.

- [x] `/compass:init` — interattivo, aiuta l'utente a definire 3–5 pilastri
      nel progetto corrente. Scrive `.compass.toml`.
- [x] `/compass:check` — calcola il Direction Index basandosi su:
    - ultimi N commit (classificati per categoria)
    - stato dei pilastri (ha file recenti?)
    - issue chiuse recenti (se `gh` è disponibile)
- [x] Schema di `.compass.toml` documentato in `docs/config.md`
- [ ] Test manuale su 3 progetti diversi: Evo-Tactics (gaming), un SaaS di
      esempio, un repo di docs *(self-test su `compass-marketplace`
      eseguito; cross-project rimane pendente)*
- [x] Skill `compass-lens` che Claude auto-invoca quando l'utente chiede
      "dove sto andando", "sono sulla strada giusta", "check del progetto"

**Criterio di done:** su un progetto con pilastri dichiarati, `/compass:check`
produce un briefing sotto i 60 secondi con numeri reali.

**Stima:** un weekend.

---

## v0.2.0 — "Boot" (kickoff direzionale)

**Scope:** il comando di apertura sessione.

- [x] `/compass:boot` — sostituisce il vecchio `/kickoff` con una versione
      direction-aware
- [x] SessionStart hook opzionale, che inietta un mini-brief (3–5 righe)
      all'apertura di ogni sessione
- [x] Integrazione **opzionale** con `claude-md-management`: se installato
      e se `.compass.toml` lo permette, `boot` può chiederne l'invocazione
      (hint emesso quando `boot.delegate_claude_md = true` + `CLAUDE.md`
      esiste; nessuna invocazione automatica)
- [x] Escape hatch `skip boot` rispettato (`COMPASS_SKIP_BOOT=1` env var
      o `boot.enabled = false`)

**Criterio di done:** aprire una sessione dentro un progetto con Compass
installato produce automaticamente un micro-brief di direzione. L'utente
può sempre disattivare o skippare.

**Stima:** mezza settimana.

---

## v0.3.0 — "Drift" (segnali di deriva)

**Scope:** identificare e riportare deriva in modo concreto.

- [x] `/compass:drift` — report dedicato con i segnali rilevati
      (script `scripts/drift.py` + skill `compass-drift`)
- [x] Classificatore commit migliorato: euristica su path + keyword
      (prefisso messaggio già presente; aggiunto **body keyword
      matching** per-categoria via `categories.*.body_keywords`).
      AI classification opzionale rinviata a v0.5.0+ (costo controllato).
- [x] Soglia configurabile: `[drift] warning_threshold` (default 50).
      Sotto soglia, `/compass:drift` emette `⚠ DRIFT WARNING`.
- [x] Output "prossimo passo di riallineamento" — `next_smallest_step`
      sempre singolo, path-specifico, non macro-task. Nuovo recency
      signal: "ultimo commit core N giorni fa (soglia drift Mgg)".

**Criterio di done:** su un progetto con 2+ settimane di deriva (molti
commit infra, zero commit core), `/compass:drift` produce un warning
chiaro + il next-action più piccolo.

**Stima:** mezza settimana.

---

## v0.4.0 — "Evolve" (il ciclo evolutivo)

**Scope:** il feedback loop dai transcript.

- [x] Lettura di `~/.claude/projects/**/*.jsonl` filtrando per progetto corrente
      (path discovery via `find_transcript_dir`, fallback su sostring match)
- [x] Statistiche: counts per pilastro + sessioni totali + menzioni
      `compass`. **Privacy-first**: solo counts, nessun contenuto estratto.
      *Boot-task hit/skip rate rinviato a v0.5.0+ (richiede tracking
      strutturato lato hook, non solo log).*
- [x] `/compass:evolve` — proposte testuali (kind: drop_pillar /
      boost_weight / add_paths_hint / noop). *Diff TOML rinviato a
      v0.5.0+ per evitare di scrivere TOML serializer custom (~50 LOC
      che spingerebbero il budget oltre 1000).*
- [ ] L'utente approva in modalità chirurgica (accept, reject, modify)
      *(v0.5.0+: richiede TOML writer + flusso `--apply`)*
- [x] Mai applicare modifiche senza consenso esplicito (no auto-apply
      in v0.4.0; user edita a mano dopo aver letto le proposte)

**Criterio di done:** dopo 10+ sessioni su un progetto, `evolve` propone
almeno 1-2 modifiche sensate al file di config.

**Stima:** 1 settimana.

---

## v0.5.0 — "Compose" (integrazioni)

**Scope:** delega ad altri plugin dell'ecosistema.

- [ ] Detection automatica dei plugin installati che Compass può sfruttare
- [ ] Interfaccia comune di delega: `delegate_to: [plugin-name]` in config
- [ ] Integrazioni documentate per:
    - [ ] `claude-md-management` (audit CLAUDE.md)
    - [ ] `claude-doctor-skill` (full health)
    - [ ] `audit-project` (Composio)
    - [ ] `agnix` (agent lint)
- [ ] Ogni integrazione è **opzionale** e **skippabile**

**Criterio di done:** in un progetto con 3+ plugin compatibili installati,
Compass li usa come subagent invece di replicare le loro funzioni.

**Stima:** 1 settimana.

---

## v0.6.0 — "Universal template"

**Scope:** rendere Compass davvero cross-project.

- [ ] Template di pilastri per tipi di progetto comuni:
    - [ ] Game dev (default: gameplay/fairness/content/tech)
    - [ ] Web SaaS (default: core funnel/perf/onboarding/reliability)
    - [ ] Research repo (default: experiments/data/writeup/reproducibility)
    - [ ] Library/SDK (default: API stability/examples/perf/compat)
- [ ] `/compass:init` può proporre il template giusto dopo aver ispezionato
      il repo
- [ ] Traduttore Evo-Tactics → progetto (tipo in `VISION.md` §5) esposto
      come `/compass:translate`

**Criterio di done:** `/compass:init` su un repo vanilla di qualsiasi tipo
produce una config iniziale ragionevole in <2 minuti.

**Stima:** 1 settimana.

---

## v1.0.0 — Public release

**Scope:** pronto per altri utenti.

- [ ] Documentazione completa in `docs/`
- [ ] 3+ casi studio documentati (progetti reali che hanno usato Compass
      per N settimane)
- [ ] Versioning semantico + changelog
- [ ] CI che valida marketplace e plugin
- [ ] Submission al [claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
      marketplace per discoverability
- [ ] Traduzione inglese del README principale (italiano resta come
      secondary language)

**Stima:** 2 settimane di polish.

---

## Fuori scope (per sempre, salvo cambio di rotta)

- ❌ UI web / dashboard
- ❌ Backend cloud / telemetria
- ❌ ML training pipelines
- ❌ Paid tier / enterprise
- ❌ Integrazione con project management tools (Linear, Jira, …)

Se uno di questi dovesse sembrare utile, ripensiamoci da zero.

---

## Principi di sviluppo

Da ripetersi ogni sprint:

1. **Lente, non sistema.** Ogni feature deve superare questo test.
2. **Compose, don't rewrite.** Se esiste già, delegare.
3. **Config > codice.** La configurabilità è il modo per essere universali,
   non il copia-incolla.
4. **Transcript > self-report.** Misuriamo l'uso reale, non quello dichiarato.
5. **Un numero dice più di 20 check.** Il Direction Index è il cuore.

---

> _"Ogni release deve rendere Compass più piccolo, non più grande."_
