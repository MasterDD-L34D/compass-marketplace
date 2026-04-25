# Vision

> _La filosofia dietro Compass, e perché esiste._

---

## 1. Origine: Evo-Tactics

Compass nasce come trasposizione universale di un tool di monitoring
costruito per [Evo-Tactics](https://github.com/MasterDD-L34D/Game), un
tactics game in sviluppo.

In Evo-Tactics il problema era concreto: l'infrastruttura (Docker, CI, Vue3,
Prisma) stava crescendo più veloce del gioco reale. I commit tecnici
sembravano progresso, ma nessuno di loro avvicinava una sessione giocabile.

La domanda diventa: **come misuri la deriva prima di accorgertene tre mesi
dopo?**

La risposta in Evo-Tactics era un **Indice di Direzione** calcolato così:

```
ID = (% commit GAMEPLAY × 0.4)
   + (pilastri coperti / totale × 0.4)
   + (issue chiuse / totale × 0.2)
```

Un singolo numero 0–100 che racconta la salute **direzionale** del progetto,
non quella ingegneristica.

Quella lente — applicata oltre al contesto gaming — è Compass.

---

## 2. I tre primitivi

Compass si appoggia su tre concetti, e basta tre:

### Pillars — cosa conta davvero

Ogni progetto ha implicitamente 3–5 cose che contano più di tutte le altre.
In un gioco sono i pilastri di design. In un SaaS potrebbero essere
conversione, retention, core funnel. In una libreria open source: API
stabilità, perf, esempi.

Il 90% dei progetti non le scrive mai. Le ha in testa, cambiano nel tempo,
e quando il team cresce si perdono.

Compass costringe a dichiararli in `.compass.toml`. Questa è la prima
scoperta utile del tool: molti progetti si accorgono che non sanno
**esattamente** cosa sono i loro pilastri finché non devono scriverli.

### Direction — quanto il lavoro serve i pilastri

Dati i pilastri dichiarati, Compass classifica il lavoro recente (commit,
issue chiuse, file modificati) in categorie:

- **Core** → tocca direttamente uno o più pilastri
- **Infra** → tooling, build, CI, dipendenze
- **Docs** → documentazione, specifiche
- **Tests** → coperture, fixture, regressioni
- **Other** → tutto il resto

La percentuale di "Core" pesata rispetto agli altri produce il
**Direction Index**.

Non è un giudizio di qualità. È un indicatore di **dove sta andando il tuo
tempo di lavoro**.

### Drift — segnali di deriva

Drift è quando i segnali dicono cose come:

- Ultimi 10 commit: 0% core, 70% infra
- Nessuna issue aperta tocca un pilastro
- Il CLAUDE.md descrive un progetto diverso da quello in git
- L'ultimo "core" commit è di 14 giorni fa

Compass fa un report breve e diretto dei segnali di drift rilevati.

---

## 3. Il ciclo evolutivo

Compass **impara dal tuo uso**. Questa è la parte "evolutiva" e va pinnata
in maniera concreta per non essere fluffy:

```
┌─────────────────────────────────────────────────────┐
│  1. Tu lavori normalmente in Claude Code            │
│  2. Hook SessionStart inietta un mini-brief         │
│  3. Se il kickoff trova poco, logga "soft session"  │
│  4. Se trova tanto, logga "hot session"             │
│  5. Dopo N sessioni, /compass:evolve propone        │
│     modifiche a .compass.toml:                      │
│       → disabilita task che non trovano mai nulla   │
│       → promuove task che trovano sempre issue      │
│       → raffina pesi dei pilastri                   │
│  6. Tu approvi o rifiuti                            │
└─────────────────────────────────────────────────────┘
```

**Nessun background agent.** Nessuna magia. Solo lettura dei
`~/.claude/projects/*.jsonl` di Claude Code e pattern-matching statistico
su quello che ha trovato.

La config è sempre **tua**. Compass propone, tu decidi.

---

## 4. Cosa Compass NON farà

Per evitare ambizione mal ripagata:

- ❌ **Non audita CLAUDE.md** → `claude-md-management` di Anthropic lo fa meglio
- ❌ **Non fa security scan** → `claude-doctor-skill` copre 46 check
- ❌ **Non valuta qualità del codice** → lint e CI esistono da 30 anni
- ❌ **Non gestisce PR / issue workflow** → GitHub/GitLab plugin lo fanno
- ❌ **Non è un orchestratore multi-agent** → `maestro-orchestrate` esiste
- ❌ **Non tiene un background LLM agent** → troppa fragilità e costo
- ❌ **Non fa ML** → puro pattern-matching sui transcript

Compass è **una lente, non un sistema**. Questa è la sua scelta principale.

---

## 5. Categorie di commit: traduzione Evo-Tactics → universale

In Evo-Tactics la classificazione era: GAMEPLAY / INFRA / TOOLING / DOCS /
DATA / ALTRO. Il peso positivo era su GAMEPLAY e DATA, perché quelli
avvicinano una sessione giocabile. INFRA era neutro o negativo se
preponderante.

Traduzione universale in Compass:

| Categoria | Pattern tipici | Peso default |
|---|---|---|
| **Core** | File dentro i path dei pilastri dichiarati | +1.0 |
| **Tests** | Test per file core; suite regression | +0.5 |
| **Docs** | README, CLAUDE.md, ADR | +0.3 |
| **Infra** | CI, Docker, build config | -0.1 |
| **Tooling** | Script interni, generator, linter config | 0 |
| **Other** | Tutto il resto | 0 |

I pesi sono modificabili in `.compass.toml`. Il default penalizza lievemente
l'infra dominante — è una scelta di game-design culture trasposta: se il
tuo tempo scarseggia, l'infrastruttura è sempre tentazione.

---

## 6. Perché metafore game-design?

Tre ragioni:

1. **Onorano l'origine**. Compass nasce in un gioco. Negarlo sarebbe
   impoverirlo.
2. **Sono più espressive**. "Drift" è più incisivo di "deviation".
   "Pillars" è più impegnativo di "guidelines". "Direction" è più netto
   di "focus".
3. **Selezionano l'utenza giusta**. Chi apprezza un tool chiamato
   "Compass" con pilastri e deriva probabilmente ragiona già in quei
   termini. Chi non li capisce probabilmente preferisce
   `claude-doctor-skill`, ed è ok.

---

## 7. Disciplina di sviluppo

Durante lo sviluppo di Compass stesso, Compass si applica a sé stesso:

- Pilastro del plugin: "**una lente, non un sistema**" — ogni feature proposta
  deve superare il test "questo è lente o è sistema?"
- Drift guard: se in una milestone la % di codice "infra" (build, CI,
  packaging) supera quella di codice "core" (analisi commit, lettura
  transcript, generazione brief), fermati e rifletti.
- Limite hardware: il plugin intero deve restare sotto ~800 LOC Python +
  ~500 righe di markdown dei comandi. Oltre, hai aggiunto sistema.

---

## 8. Ringraziamenti e prior art

Compass compone, non riscrive. Chi rispetto:

- [claude-md-management](https://claude.com/plugins/claude-md-management) — Anthropic ufficiale
- [claude-doctor-skill](https://github.com/SomeStay07/claude-doctor-skill) — 46 check, 6 layer, adaptive scoring
- [agnix](https://github.com/avifenesh/AgentSys) — linter per agent config
- [homunculus](https://github.com/rohitg00/awesome-claude-code-toolkit) — self-evolving approach, utile come studio di caso
- Filosofia di design da **Final Fantasy Tactics** (leggibilità), **Spore**
  (evoluzione emergente) e il GDD di **Evo-Tactics** v0.1

---

> _"La deriva non si vede quando succede. Si vede dopo, quando è tardi.
> Compass è il termometro prima della febbre."_
