---
name: lens
description: Direction-aware project lens. Use proactively when the user asks "where am I going", "am I on track", "is my work serving my goals", "sono sulla strada giusta", "dove sto andando", "check del progetto", or expresses doubt about whether recent commits matter. Triggers /compass:check under the hood.
allowed-tools: Bash
---

# Compass lens — when the user wonders if they're drifting

This skill is auto-invoked by Claude when the user asks direction-aware
questions even without saying "compass" explicitly. Phrases that should
trigger it:

- "Where am I going with this project?"
- "Am I on track?" / "Sono sulla strada giusta?"
- "Is this work meaningful?" / "Sto andando da qualche parte?"
- "Check the project" / "Fammi un check"
- "Is the last week useful?"

## What to do

1. Check that `.compass.toml` exists at the repo root. If not, suggest
   `/compass:init` and stop.
2. Run the Direction Index briefing:

   ```!
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/check.py"
   ```

3. Present the briefing verbatim. Don't add interpretation unless the
   user asks for it.
4. If the user asks "what should I do next?", point at the **Next
   smallest step** line in the briefing — that's already the answer.

## What NOT to do

- Don't compute the Index by hand. Use the script.
- Don't narrate the breakdown table. The numbers speak.
- Don't suggest a refactor or a sprint. Compass is a lens, not a plan.
