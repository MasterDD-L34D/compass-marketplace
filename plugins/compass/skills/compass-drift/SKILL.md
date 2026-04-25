---
name: drift
description: Drift-focused report. Lists detected drift signals (up to 5), emits a warning if Direction Index falls below the configured threshold, and proposes the smallest realignment step. Use when the user says "drift report", "compass drift", "find drift", "deriva del progetto", "sto andando alla deriva", or wants only the drift slice without the full /compass:check briefing.
allowed-tools: Bash
---

# /compass:drift — segnali di deriva

Focused subset of `/compass:check`: only drift signals + warning gate +
next realignment step. Useful when the user wants to know "what's
pulling me away from the pillars" without the full breakdown table.

```!
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/drift.py"
```

Present output verbatim. The script emits a hard `⚠ DRIFT WARNING`
header when DI < `drift.warning_threshold` (default 50). Otherwise it
confirms the project is above threshold and lists any sub-threshold
signals as informational.

The next step is **always the smallest possible** realignment, not a
macro-task. If you want a broader strategic view, use `/compass:check`.
