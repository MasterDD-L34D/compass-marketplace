"""Tests for classify_commit() verification logic — issue #9 regression suite."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.classify import classify_commit

_CFG = {
    "pillars": [
        {"id": "memory", "paths": ["*.md"], "weight": 1.0, "name": "memory", "description": ""},
        {"id": "engine", "paths": ["lib/**"], "weight": 1.0, "name": "engine", "description": ""},
    ],
    "categories": {
        "core":    {"paths": [], "weight": 1.0,  "message_patterns": [r"^(feat|fix|refactor|perf)(\(.+\))?!?:"], "body_keywords": []},
        "tests":   {"paths": ["tests/**"], "weight": 0.5, "message_patterns": [], "body_keywords": []},
        "docs":    {"paths": ["docs/**", "**/*.md"], "weight": 0.3, "message_patterns": [r"^docs(\(.+\))?:"], "body_keywords": ["pilastro", "manifest", "vision"]},
        "infra":   {"paths": [".github/**"], "weight": -0.1, "message_patterns": [], "body_keywords": []},
        "tooling": {"paths": ["scripts/**"], "weight": 0.0, "message_patterns": [], "body_keywords": []},
    },
    "ignore": [],
}


def _commit(sha, message, files):
    return {"sha": sha, "message": message, "ts": 0, "files": files}


def test_pillar_md_docs_core_is_verified():
    # chore(memory) with body keyword "pilastro" touching INDEX.md (pillar:memory, .md)
    # msg_cat=docs, dominant=core — structural co-occurrence, not a real conflict
    c = classify_commit(
        _commit("aaa", "chore(memory): handoff\n\naggiornamento pilastro memoria", ["INDEX.md"]),
        _CFG,
    )
    assert c.dominant_category == "core"
    assert c.verified is True


def test_feat_code_pillar_verified():
    # feat: touching lib/classify.py (pillar:engine) — msg_cat=core matches dominant=core
    c = classify_commit(
        _commit("bbb", "feat: add classifier", ["lib/classify.py"]),
        _CFG,
    )
    assert c.dominant_category == "core"
    assert c.verified is True


def test_docs_non_md_pillar_still_flagged():
    # docs: touching lib/foo.py (pillar:engine, NOT .md) — msg_cat=docs, dominant=core
    # pillar file is .py, so pillar_md_only=False → real conflict, still verified=False
    c = classify_commit(
        _commit("ccc", "docs: update api reference", ["lib/foo.py"]),
        _CFG,
    )
    assert c.dominant_category == "core"
    assert c.verified is False
