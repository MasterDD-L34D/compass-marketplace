# `.compass.toml` — schema di configurazione

> Documento normativo per la v0.1.0. Schema minimale. Ogni campo ha un
> default ragionevole: un `.compass.toml` valido può essere lungo 10 righe.
>
> **Formato**: TOML (parsato con `tomllib`, stdlib Python ≥ 3.11).
> **Decisione** in §7.

---

## 1. Posizione e formato

- **Path**: `.compass.toml` nella root del progetto utente (stesso livello
  di `.git/`).
- **Formato**: [TOML 1.0.0](https://toml.io/en/v1.0.0).
- **Parser**: `tomllib` (Python stdlib, ≥ 3.11). Zero dipendenze.
- **Writer (in `/compass:init`)**: emissione via template string + check
  di round-trip con `tomllib.loads` prima di scrivere.
- **Encoding**: UTF-8, LF.
- **Versione schema**: campo `version` obbligatorio. v0.1.0 → `version = 1`.

## 2. Schema completo (con default)

```toml
# Versione dello schema. Obbligatorio. v0.1.0 scrive e legge solo
# `version = 1`.
version = 1

# Metadati del progetto. Il `type` influenza solo i template di init.
[project]
name = "compass-marketplace"    # default: nome della directory root
type = "library"                # one of: game-dev | web-saas | research
                                #         library | docs | other
                                # default: "other"

# I pilastri. 3-5 raccomandati. Minimo 1, massimo 10.
# Ogni pilastro è una `[[pillars]]` table entry (array-of-tables TOML).
# L'id deve essere kebab-case unico.
[[pillars]]
id = "direction-lens"
name = "Direction Index & pillars core"
description = "Il cuore del plugin: lente, non sistema."
paths = [                        # path glob (fnmatch-style, POSIX)
  "plugins/compass/commands/**",
  "plugins/compass/skills/**",
  "plugins/compass/scripts/**",
]
weight = 1.0                     # default 1.0. Relativo agli altri pilastri.

[[pillars]]
id = "docs-governance"
name = "Governance dei documenti"
description = "VISION/ROADMAP/CLAUDE come fonti di verità."
paths = ["VISION.md", "ROADMAP.md", "CLAUDE.md", "docs/**"]
weight = 0.7

# Categorie di classificazione. I path delle categorie sono
# **complementari** ai pilastri: un file che matcha un pilastro è sempre
# "core", anche se matcherebbe anche "docs". Regola di matching:
# first-match wins nell'ordine [pillars → core → tests → docs → infra
# → tooling → other].

[categories.core]
# Se vuoto (default), derivato implicitamente dall'unione dei
# `pillars[].paths`. Può essere esteso qui per path "core ma non
# associati a un pilastro specifico" (raro, sconsigliato).
paths = []
weight = 1.0
message_patterns = ["^feat", "^feature"]   # opzionale. Default [].

[categories.tests]
paths = ["tests/**", "**/*_test.py", "**/*.test.*", "**/*.spec.*"]
weight = 0.5
message_patterns = ["^test"]

[categories.docs]
paths = ["docs/**", "**/*.md", "README*", "LICENSE*"]
weight = 0.3
message_patterns = ["^docs?"]

[categories.infra]
paths = [".github/**", "Dockerfile*", "docker-compose*", "ci/**",
         ".gitlab-ci.yml", "Makefile"]
weight = -0.1                    # leggera penalità se prevalente
message_patterns = ["^ci", "^build"]

[categories.tooling]
paths = ["scripts/**", "tools/**", ".pre-commit-config.yaml"]
weight = 0.0
message_patterns = ["^chore"]

# "other" è sempre l'ultimo, non configurabile, peso 0.

# Direction Index (0-100). Formula (vedi VISION.md §1, tradotta
# in universale):
#   ID = core_share      * 40
#      + pillar_coverage * 40
#      + issue_factor    * 20
[direction]
window = 30                      # commit da analizzare. default 30.
                                 # range: 5..500.

[direction.formula]
core_share = 0.4
pillar_coverage = 0.4
issue_factor = 0.2

[direction.thresholds]
healthy = 60                     # >= 60: "rotta coerente"
warning = 40                     # < 40: "deriva evidente"
                                 # 40-59: "attenzione"

# Integrazione con GitHub issues (opzionale, v0.1.0 read-only).
# Se `gh` CLI non disponibile o `enabled = false`, issue_factor = 0.5
# (neutro).
[issues]
enabled = false
closed_window_days = 30

# Path esclusi dall'analisi (rumore tipico).
ignore = [
  ".git/**",
  "node_modules/**",
  "**/__pycache__/**",
  "*.lock",
  "dist/**",
  "build/**",
]

# Boot — kickoff direzionale opzionale (v0.2.0+).
[boot]
enabled = true                   # SessionStart hook injects mini-brief?
                                 # default true. False = hook silenzioso.
delegate_claude_md = false       # se true e claude-md-management è
                                 # installato, boot suggerisce di
                                 # invocarlo quando il CLAUDE.md è stale.
escape_env = "COMPASS_SKIP_BOOT" # nome env var che disabilita il hook
                                 # per la sessione corrente (qualsiasi
                                 # valore non vuoto skippa).

# Drift — soglia warning + feature flag (v0.3.0+).
[drift]
warning_threshold = 50           # DI sotto questa soglia → /compass:drift
                                 # emette warning. Range 0..100.
                                 # Indipendente da direction.thresholds:
                                 # quelle classificano (healthy/warning/
                                 # deriva), questa è il trigger di alert.
recency_days = 7                 # "ultimo commit core a > N giorni" è
                                 # un drift signal. Default 7.

# Forward-compat. v0.1.0+ legge ma ignora.
[evolve]
enabled = false                  # v0.4.0

delegate_to = []                 # v0.5.0
```

## 3. Minimal valid file

```toml
version = 1

[[pillars]]
id = "core"
name = "Core product"
paths = ["src/**"]
```

Tutto il resto usa i default. Direction Index calcolabile.

## 4. Regole di validazione (applicate da `init` e `check`)

| Campo | Vincolo |
|---|---|
| `version` | deve essere `1` (int) |
| `pillars` | 1 ≤ len ≤ 10 |
| `pillars[].id` | kebab-case, unico, regex `^[a-z][a-z0-9-]{1,40}$` |
| `pillars[].paths` | len ≥ 1, ogni path non vuoto, string |
| `pillars[].weight` | 0.0 ≤ w ≤ 10.0, default 1.0 |
| `direction.window` | 5 ≤ w ≤ 500 |
| `direction.formula.*` | somma dei 3 pesi = 1.0 ± 0.001 |
| `direction.thresholds.healthy` | `> warning`, entrambi in [0, 100] |
| `project.type` | uno di: game-dev, web-saas, research, library, docs, other |
| `categories.*.weight` | -1.0 ≤ w ≤ 2.0 |
| `categories.*.message_patterns` | list di stringhe regex valide (opzionale) |

Violazioni → `check` stampa errore specifico con riga TOML e esce non-zero.
`init` rigetta input invalidi e richiede correzione.

## 5. Path matching

- **Stile glob**: fnmatch POSIX esteso con `**` (qualsiasi numero di
  segmenti). Case-sensitive. Relativo alla root del progetto. Sintassi
  deliberatamente allineata a `CODEOWNERS` / `.gitignore` per leva
  cognitiva: chi sa scrivere quelli sa scrivere pillar.paths.
- **Ordine di match**: per ogni file del commit, si tenta in ordine
  (**first-match wins**, non last-match come CODEOWNERS — mentalmente più
  semplice):
  1. Tutti i `[[pillars]].paths` (in ordine di dichiarazione). Primo
     match → file è "core" + associato a quel pilastro (per pillar_coverage).
  2. `categories.core.paths` espliciti.
  3. `categories.tests.paths`.
  4. `categories.docs.paths`.
  5. `categories.infra.paths`.
  6. `categories.tooling.paths`.
  7. Fallback: `other`.
- **Ignore**: i path che matchano `ignore` sono scartati prima del match.

### 5.1 Segnale secondario: commit message prefix + body keywords (opzionale)

Classificazione ibrida path + messaggio. Per ogni commit, due segnali
testuali aggiuntivi alla path-based:

1. **Prefisso prima riga messaggio** (stile semantic-release). Per ogni
   categoria, lista `message_patterns` di regex.
2. **Body keywords** (v0.3.0+). Per ogni categoria, lista
   `body_keywords` di parole/frasi case-insensitive cercate nel corpo
   del commit (righe 2..N), non solo nella prima riga. Utile per
   commit con messaggi tipo "fix: typo \\n\\n closes #42, related to
   onboarding flow". I keyword corrispondenti riportano il commit alla
   categoria associata anche quando path/prefisso non bastano.

Per ogni commit, se prefisso o keyword matcha un pattern, si applica
la regola di conferma:

Regola:
- Se la category dominante del commit (per score pesato dei file) **concorda**
  con la category che matcha il prefisso del messaggio → peso × 1.0
  ("verified").
- Se **discorda** (es. `feat:` ma file tutti in `.github/`) → peso × 0.5
  ("ambiguous commit": squalifica parziale).
- Se nessun pattern matcha → neutro, peso × 1.0.

Default: tutti `message_patterns` vuoti → segnale disabilitato,
classificazione pure-path. Utenti che seguono Conventional Commits lo
abilitano esplicitamente.

## 6. Unità di calcolo

Un commit con N file modificati contribuisce con **N voti pesati**:

```
score(file)  = category.weight  (della categoria a cui appartiene)
core_share   = sum(score di file core) / sum(|score| di tutti i file)
```

Il motivo per cui usiamo **file** e non commit: un commit che tocca 1 file
core e 50 file infra non è "50% core". È "per lo più infra che passa
vicino al core". La granularità file è più onesta.

`pillar_coverage` invece conta pilastri unici toccati almeno una volta nel
window, indipendentemente dal peso.

`issue_factor = closed_issues / max(1, total_issues)` nel window temporale,
solo se `issues.enabled = true` e `gh` CLI disponibile. Altrimenti 0.5.

## 7. Decisione tecnica: TOML, non YAML

TOML adottato per v0.1.0. Ragioni:

| Vincolo | YAML | JSON | **TOML** |
|---|---|---|---|
| Python stdlib parser | ❌ (nessuno) | ✅ `json` | ✅ `tomllib` (3.11+) |
| Commenti | ✅ | ❌ | ✅ |
| Writability umana | ✅ | ❌ (quote-all) | ✅ |
| Complessità parser nostro | ~200 LOC ad-hoc | 0 | 0 |
| Rischio bug parser | alto | 0 | 0 |

**Costo di TOML**:
- Sintassi `[[pillars]]` array-of-tables nuova per chi non ha mai usato
  `pyproject.toml` / `Cargo.toml`. Imparabile in 30 secondi.
- Richiede Python **3.11+** (ottobre 2022). Bump dalla soglia `3.8+`
  dichiarata inizialmente in `CLAUDE.md`.

**Benefici**:
- Zero LOC di parser code nel plugin.
- Zero surface per bug subtili di parsing (errori di indentazione,
  ambiguità scalari).
- Tipizzazione forte (int vs float vs bool vs string non ambigua).
- Spec formale (toml.io) — nessun "sottoinsieme Compass" da documentare.

Scartato: parser YAML subset ad-hoc (rischioso), JSON (no commenti,
inumano), JSONC (riscrivere parser comunque per strippare commenti).

Il nome `.compass.toml` sostituisce `.compass.yaml` dei documenti
precedenti (VISION/ROADMAP). Aggiornamento atomico di quei documenti
richiesto nella stessa PR di v0.1.0.

## 8. Esempio realistico (compass-marketplace)

```toml
version = 1

[project]
name = "compass-marketplace"
type = "library"

[[pillars]]
id = "direction-lens"
name = "Direction Index core"
description = "Commands init/check + skill di lente."
paths = [
  "plugins/compass/commands/**",
  "plugins/compass/skills/**",
  "plugins/compass/scripts/**",
  "plugins/compass/lib/**",
]
weight = 1.0

[[pillars]]
id = "docs-truth"
name = "Documenti canonici"
description = "VISION/ROADMAP/CLAUDE come fonti di verità."
paths = ["VISION.md", "ROADMAP.md", "CLAUDE.md", "docs/**"]
weight = 0.7

[[pillars]]
id = "manifest-validity"
name = "Manifest plugin & marketplace"
description = "I due plugin.json e marketplace.json valid."
paths = [
  ".claude-plugin/marketplace.json",
  "plugins/*/plugin.json",
  "plugins/*/.claude-plugin/plugin.json",
]
weight = 0.5

[direction]
window = 30

[issues]
enabled = true
closed_window_days = 30
```

## 9. Output contract di `/compass:check`

Il briefing deve essere **decomposto**, non monolitico (lezione da
claude-doctor-skill: un singolo numero senza breakdown non è azionabile).

Struttura minima del report markdown:

```
# Compass — Direction check

**Direction Index: 67 / 100** ·  window: 30 commits · generated: 2026-04-25

## Breakdown
| Componente       | Peso | Valore | Contributo |
|------------------|-----:|-------:|-----------:|
| Core share       | 0.40 |    58% |       23.2 |
| Pillar coverage  | 0.40 |   3/4  |       30.0 |
| Issue factor     | 0.20 |   0.69 |       13.8 |

## Pilastri nel window
- [x] direction-lens (12 commit, 45% peso)
- [x] docs-truth (8 commit, 25% peso)
- [x] manifest-validity (2 commit, 8% peso)
- [ ] **untouched-pillar** ← 0 commit in 30 commit

## Drift signals (ranked)
1. `docs-truth` ha avuto 0 commit negli ultimi 10 giorni (peso alto).
2. 40% dei commit in window sono `infra` (normalmente <10%).

## Next smallest step
Apri un commit su `untouched-pillar`. Il path più promettente:
`plugins/compass/skills/compass-lens/` (vuoto attualmente).
```

Vincoli obbligatori sull'output:
- **Sempre** mostra breakdown. DI senza breakdown è vietato.
- **Ranked drift signals**: top 3, ordinati per impatto su DI.
- **Next smallest step**: 1 azione concreta, path specifico se possibile.
- Lunghezza totale ≤ 40 righe markdown. Lente, non report.

## 10. Cosa lo schema NON fa

- Non dichiara autori, branch protetti, dipendenze. (Non è Compass.)
- Non definisce workflow CI. (Non è Compass.)
- Non schedula cron / notifiche. (Non è Compass.)
- Non descrive un DAG di task. (Non è Compass.)

Se ti viene voglia di aggiungere qualcosa qui, rileggi `VISION.md §4`.
