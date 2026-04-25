#!/usr/bin/env bash
# bootstrap.sh — inizializza il repo compass-marketplace su GitHub
#
# Uso:
#   1. Crea un repo vuoto su github.com (es. MasterDD-L34D/compass-marketplace)
#      senza README/gitignore/LICENSE (ce li abbiamo già)
#   2. Lancia questo script dalla root dell'archivio estratto:
#        bash bootstrap.sh git@github.com:MasterDD-L34D/compass-marketplace.git
#
# Richiede: git, ssh-key configurata (o cambia in https URL)

set -euo pipefail

REMOTE="${1:-}"
if [ -z "$REMOTE" ]; then
  echo "Uso: bash bootstrap.sh <git-remote-url>"
  echo "Esempio: bash bootstrap.sh git@github.com:MasterDD-L34D/compass-marketplace.git"
  exit 1
fi

if [ ! -f ".claude-plugin/marketplace.json" ]; then
  echo "Errore: devi lanciare lo script dalla root del marketplace (dove c'è .claude-plugin/marketplace.json)"
  exit 1
fi

# Init se non già fatto
if [ ! -d ".git" ]; then
  git init -b main
fi

git add .
git commit -m "chore: bootstrap compass-marketplace v0.0.1

- marketplace.json + plugin.json manifests
- README + VISION + ROADMAP
- LICENSE (MIT) + .gitignore
- scaffolding for commands/agents/skills/hooks

Direction-first audit lens for Claude Code projects.
Born from Evo-Tactics design philosophy.

Next: v0.1.0 MVP (see ROADMAP.md)"

git remote add origin "$REMOTE" 2>/dev/null || git remote set-url origin "$REMOTE"
git push -u origin main

echo ""
echo "✓ Marketplace pushato su $REMOTE"
echo ""
echo "Prossimi passi:"
echo "  1. Dal tuo terminale Claude Code:"
echo "     /plugin marketplace add MasterDD-L34D/compass-marketplace"
echo "  2. Verifica che venga riconosciuto:"
echo "     /plugin marketplace list"
echo "  3. Il plugin compass sarà installabile ma ancora senza comandi (è v0.0.1)"
echo ""
echo "Inizia v0.1.0 quando sei pronto — vedi ROADMAP.md"
