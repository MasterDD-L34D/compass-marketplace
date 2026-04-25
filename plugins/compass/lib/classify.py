"""Classify files and commits. Spec: docs/config.md §5-§6."""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from typing import Any

from .config import CATEGORY_ORDER


@dataclass
class FileHit:
    path: str
    category: str
    pillar_id: str | None
    weight: float


@dataclass
class CommitHit:
    sha: str
    message: str
    ts: int = 0
    files: list[FileHit] = field(default_factory=list)
    dominant_category: str | None = None
    verified: bool = True


def _glob_match(path: str, pat: str) -> bool:
    """fnmatch with ** support (any number of segments)."""
    if "**" not in pat:
        return fnmatch.fnmatchcase(path, pat)
    parts: list[str] = []
    i = 0
    while i < len(pat):
        c = pat[i]
        if c == "*" and i + 1 < len(pat) and pat[i + 1] == "*":
            parts.append(".*")
            i += 2
            if i < len(pat) and pat[i] == "/":
                i += 1
        elif c == "*":
            parts.append("[^/]*"); i += 1
        elif c == "?":
            parts.append("[^/]"); i += 1
        elif c in ".+^$()[]{}|\\":
            parts.append(re.escape(c)); i += 1
        else:
            parts.append(c); i += 1
    return re.match("^" + "".join(parts) + "$", path) is not None


def _match_any(path: str, patterns: list[str]) -> bool:
    return any(_glob_match(path, p) for p in patterns)


def is_ignored(path: str, ignore_patterns: list[str]) -> bool:
    return _match_any(path, ignore_patterns)


def classify_file(path: str, cfg: dict[str, Any]) -> FileHit:
    """Resolve path to FileHit. Pillars first (first-match wins), then categories, then 'other'."""
    for p in cfg["pillars"]:
        if _match_any(path, p["paths"]):
            return FileHit(path, f"pillar:{p['id']}", p["id"],
                           cfg["categories"]["core"]["weight"])
    for cat_name in CATEGORY_ORDER:
        cat = cfg["categories"][cat_name]
        if _match_any(path, cat["paths"]):
            return FileHit(path, cat_name, None, cat["weight"])
    return FileHit(path, "other", None, 0.0)


def _category_from_message(message: str, cfg: dict[str, Any]) -> str | None:
    if not message:
        return None
    lines = message.splitlines()
    head, body = lines[0], "\n".join(lines[1:]).lower()
    for cat_name in CATEGORY_ORDER:
        cat = cfg["categories"][cat_name]
        for pat in cat["message_patterns"]:
            try:
                if re.search(pat, head):
                    return cat_name
            except re.error:
                pass
        if body and any(kw and kw.lower() in body for kw in cat["body_keywords"]):
            return cat_name
    return None


def classify_commit(commit: dict[str, Any], cfg: dict[str, Any]) -> CommitHit:
    """Classify commit's files + resolve dominant category + verify against message."""
    hits = [classify_file(f, cfg) for f in commit.get("files", [])
            if not is_ignored(f, cfg["ignore"])]
    ch = CommitHit(sha=commit["sha"], message=commit.get("message", ""),
                   ts=int(commit.get("ts", 0)), files=hits)
    if not hits:
        return ch
    weights: dict[str, float] = {}
    for h in hits:
        key = "core" if h.category.startswith("pillar:") else h.category
        weights[key] = weights.get(key, 0.0) + abs(h.weight)
    ch.dominant_category = max(weights.items(), key=lambda kv: kv[1])[0]
    msg_cat = _category_from_message(ch.message, cfg)
    if msg_cat is not None and msg_cat != ch.dominant_category:
        ch.verified = False
    return ch
