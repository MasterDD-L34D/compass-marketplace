"""Load + validate + default-fill .compass.toml. Spec: docs/config.md."""
from __future__ import annotations
import re, tomllib
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
VALID_PROJECT_TYPES = {"game-dev", "web-saas", "research", "library", "docs", "other"}
PILLAR_ID_RE = re.compile(r"^[a-z][a-z0-9-]{1,40}$")


class ConfigError(ValueError):
    """Raised on invalid .compass.toml content."""


_CAT_DEFAULTS = (
    ("core",    [], 1.0),
    ("tests",   ["tests/**", "**/*_test.py", "**/*.test.*", "**/*.spec.*"], 0.5),
    ("docs",    ["docs/**", "**/*.md", "README*", "LICENSE*"], 0.3),
    ("infra",   [".github/**", "Dockerfile*", "docker-compose*", "ci/**",
                 ".gitlab-ci.yml", "Makefile"], -0.1),
    ("tooling", ["scripts/**", "tools/**", ".pre-commit-config.yaml"], 0.0),
)
DEFAULTS: dict[str, Any] = {
    "project": {"name": None, "type": "other"},
    "categories": {n: {"paths": p, "weight": w, "message_patterns": []}
                   for n, p, w in _CAT_DEFAULTS},
    "direction": {"window": 30,
                  "formula": {"core_share": 0.4, "pillar_coverage": 0.4, "issue_factor": 0.2},
                  "thresholds": {"healthy": 60, "warning": 40}},
    "issues": {"enabled": False, "closed_window_days": 30},
    "ignore": [".git/**", "node_modules/**", "**/__pycache__/**",
               "*.lock", "dist/**", "build/**"],
    "boot": {"enabled": True, "delegate_claude_md": False,
             "escape_env": "COMPASS_SKIP_BOOT"},
    "evolve": {"enabled": False},
    "delegate_to": [],
}

CATEGORY_ORDER = tuple(n for n, _, _ in _CAT_DEFAULTS)


def load(path: Path) -> dict[str, Any]:
    """Read + parse + validate + default-fill. Raises ConfigError on bad data."""
    if not path.exists():
        raise ConfigError(f"config not found: {path}")
    try:
        with path.open("rb") as f:
            raw = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path}: TOML parse error: {e}") from e
    cfg = _merge_defaults(raw); _validate(cfg, path); return cfg


def _merge_defaults(raw: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "version": raw.get("version"),
        "pillars": list(raw.get("pillars", [])),
        "project": {**DEFAULTS["project"], **raw.get("project", {})},
        "direction": _deep_merge(DEFAULTS["direction"], raw.get("direction", {})),
        "issues": {**DEFAULTS["issues"], **raw.get("issues", {})},
        "ignore": list(raw.get("ignore", DEFAULTS["ignore"])),
        "boot": {**DEFAULTS["boot"], **raw.get("boot", {})},
        "evolve": {**DEFAULTS["evolve"], **raw.get("evolve", {})},
        "delegate_to": list(raw.get("delegate_to", [])),
        "categories": {},
    }
    raw_cats = raw.get("categories", {})
    for name, default in DEFAULTS["categories"].items():
        user = raw_cats.get(name, {})
        out["categories"][name] = {
            "paths": list(user.get("paths", default["paths"])),
            "weight": float(user.get("weight", default["weight"])),
            "message_patterns": list(user.get("message_patterns", default["message_patterns"])),
        }
    return out


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in override.items():
        out[k] = _deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def _err(path: Path, msg: str) -> None:
    raise ConfigError(f"{path}: {msg}")


def _validate(cfg: dict[str, Any], path: Path) -> None:
    if cfg.get("version") != SCHEMA_VERSION:
        _err(path, f"version must be {SCHEMA_VERSION} (got {cfg.get('version')!r})")
    pillars = cfg["pillars"]
    if not isinstance(pillars, list) or not 1 <= len(pillars) <= 10:
        _err(path, f"pillars must be 1..10 entries (got {len(pillars)})")
    seen: set[str] = set()
    for i, p in enumerate(pillars):
        if not isinstance(p, dict):
            _err(path, f"pillars[{i}] must be a table")
        pid = p.get("id", "")
        if not isinstance(pid, str) or not PILLAR_ID_RE.match(pid):
            _err(path, f"pillars[{i}].id invalid kebab-case: {pid!r}")
        if pid in seen:
            _err(path, f"pillars[{i}].id duplicate: {pid!r}")
        seen.add(pid)
        paths = p.get("paths", [])
        if not isinstance(paths, list) or not paths or not all(isinstance(x, str) and x for x in paths):
            _err(path, f"pillars[{i}].paths must be non-empty list of strings")
        w = p.get("weight", 1.0)
        if not isinstance(w, (int, float)) or not 0.0 <= w <= 10.0:
            _err(path, f"pillars[{i}].weight out of [0.0, 10.0]: {w!r}")
        p["weight"] = float(w)
        p.setdefault("name", pid)
        p.setdefault("description", "")
    ptype = cfg["project"].get("type", "other")
    if ptype not in VALID_PROJECT_TYPES:
        _err(path, f"project.type invalid: {ptype!r}")
    d = cfg["direction"]
    if not isinstance(d["window"], int) or not 5 <= d["window"] <= 500:
        _err(path, f"direction.window out of [5,500]: {d['window']!r}")
    f = d["formula"]
    total = f["core_share"] + f["pillar_coverage"] + f["issue_factor"]
    if abs(total - 1.0) > 0.001:
        _err(path, f"direction.formula weights must sum to 1.0 (got {total:.4f})")
    t = d["thresholds"]
    if not 0 <= t["warning"] < t["healthy"] <= 100:
        _err(path, f"direction.thresholds invalid: warning={t['warning']} healthy={t['healthy']}")
    for name, cat in cfg["categories"].items():
        cw = cat["weight"]
        if not isinstance(cw, (int, float)) or not -1.0 <= cw <= 2.0:
            _err(path, f"categories.{name}.weight out of [-1.0, 2.0]: {cw!r}")
        for pat in cat["message_patterns"]:
            try:
                re.compile(pat)
            except re.error as e:
                _err(path, f"categories.{name}.message_patterns invalid regex {pat!r}: {e}")


def find_config(start: Path) -> Path | None:
    """Walk up from start looking for .compass.toml."""
    cur = start.resolve()
    for parent in (cur, *cur.parents):
        c = parent / ".compass.toml"
        if c.exists():
            return c
    return None
