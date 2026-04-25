# Compass Marketplace

> **Direction-first audit & kickoff lens per Claude Code.**
> Una filosofia nata in Evo-Tactics, applicata a qualsiasi progetto.

---

## Cos'è

`compass` è un plugin Claude Code minimale che aggiunge **una sola cosa**
all'ecosistema: una **lente direzionale** sul tuo progetto.

Non un altro "project doctor", non un altro audit generico. Quelli esistono
già e sono ottimi (vedi [Ecosistema](#ecosistema-e-integrazioni) sotto).

Compass misura una cosa sola che nessun altro tool misura bene:

> _Quanto il lavoro recente del progetto serve i suoi pilastri?_

Risponde con un numero (**Direction Index** 0–100) e con segnali concreti di
**drift** (deriva dai pilastri). Poi propone il prossimo passo più piccolo che
ti riallinea.

---

## A chi serve

A chi lavora su progetti dove **facile perdere la rotta** perché:

- ci sono tanti piani paralleli (infra / UX / core / test / docs)
- il perimetro del "core" è fumoso o cambia nel tempo
- il rapporto tra ciò che si costruisce e ciò che conta davvero non è ovvio
- l'infrastruttura può crescere più del prodotto senza che nessuno se ne accorga

Casi d'uso originali: game dev (**Evo-Tactics**), research repo, design system,
prodotti in early-stage con MVP ancora da definire, monorepo con team multipli.

Casi d'uso dove non serve: bugfix sprint, libreria matura e congelata,
progetti pre-confezionati con roadmap rigida.

---

## Stato attuale

🏗️ **Pre-alpha.** Questo repository contiene per ora solo:

- manifest e scaffolding del plugin
- la visione (`VISION.md`)
- la roadmap incrementale (`ROADMAP.md`)

**Niente codice eseguibile ancora.** La scelta è voluta: piantiamo la bandiera
filosofica prima di sporcarci le mani. Vedi [ROADMAP.md](ROADMAP.md) per le
milestone.

---

## Installazione (quando sarà pronto)

```bash
# Una volta, dal tuo terminale Claude Code
/plugin marketplace add MasterDD-L34D/compass-marketplace

# Installa il plugin
/plugin install compass@compass-marketplace

# Primo uso
/compass init
```

Nella v0.0.1 corrente l'installazione funziona come test ma i comandi non
sono ancora implementati — parte dalla v0.1.0.

---

## Anteprima dei comandi (target)

```
/compass init       → interattivo, definisce i pilastri del progetto
/compass check      → Direction Index + stato pilastri (briefing <1 min)
/compass boot       → kickoff direzionale: briefing + deleghe ai plugin giusti
/compass drift      → cerca segnali di deriva nei commit/issue recenti
/compass evolve     → legge i transcript, propone modifiche a .compass.yaml
```

Plus un `SessionStart` hook opzionale che inietta un mini-brief all'apertura.

Dettagli in [VISION.md](VISION.md).

---

## Ecosistema e integrazioni

Compass **non riscrive** queste funzioni — le delega:

| Quello che ti serve | Chi lo fa (già) | Compass cosa fa |
|---|---|---|
| Audit di CLAUDE.md | [`claude-md-management`](https://claude.com/plugins/claude-md-management) (Anthropic) | Lo chiama nel `boot` se installato |
| Project health a 360° | [`claude-doctor-skill`](https://github.com/SomeStay07/claude-doctor-skill) | Lo suggerisce, non lo duplica |
| Full project audit | `audit-project` (Composio) | Lo delega in modalità heavy |
| Lint degli agent | `agnix` (AgentSys) | Complementare, può essere chiamato |

Il principio: **compose, don't rewrite.**

---

## Filosofia in 3 righe

1. **Pilastri** — dichiari cosa conta davvero nel progetto (3–5 cose)
2. **Direction** — il tool misura quanto il lavoro recente serve i pilastri
3. **Drift** — segnala quando stai derivando, propone il passo di riallineamento

Nient'altro. Questo è il differenziale.

Origine della lente: [VISION.md](VISION.md).

---

## License

MIT. Vedi [LICENSE](LICENSE).

---

## Contribuire

Non ancora. Finché siamo in pre-alpha, la superficie API è troppo fluida per
accettare PR. Segui la roadmap o apri una discussion se hai un caso d'uso
che pensi meriti di entrare nei pilastri di default del tool.
