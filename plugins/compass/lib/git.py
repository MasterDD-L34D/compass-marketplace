"""Read recent commits via `git` CLI. No external deps."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class GitError(RuntimeError):
    """Raised on git CLI errors."""


def _run(args: list[str], cwd: Path) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
        )
    except FileNotFoundError as e:
        raise GitError("git CLI not found in PATH") from e
    except subprocess.CalledProcessError as e:
        raise GitError(f"git {' '.join(args)} failed: {e.stderr.strip()}") from e
    return out.stdout


def repo_root(start: Path) -> Path:
    """Resolve git repo root from `start`. Raises GitError if not a repo."""
    out = _run(["rev-parse", "--show-toplevel"], cwd=start).strip()
    if not out:
        raise GitError(f"{start} is not inside a git repo")
    return Path(out)


def recent_commits(repo: Path, window: int) -> list[dict[str, Any]]:
    """Return last `window` commits, each as {sha, author, ts, message, files}.

    Uses `git log -n <window> --name-only --format=...` with a unique record
    delimiter so multiline messages parse safely.
    """
    sep = "\x1ecompassREC\x1e"
    field = "\x1ecompassFLD\x1e"
    fmt = field.join(["%H", "%an", "%at", "%s%n%b"])
    raw = _run(
        ["log", f"-n{window}", "--name-only",
         f"--pretty=format:{sep}{fmt}{sep}"],
        cwd=repo,
    )
    commits: list[dict[str, Any]] = []
    chunks = raw.split(sep)
    # chunks alternate: ["", header1, files1, header2, files2, ...]
    i = 1
    while i < len(chunks):
        header = chunks[i]
        files_blob = chunks[i + 1] if i + 1 < len(chunks) else ""
        i += 2
        parts = header.split(field, 3)
        if len(parts) < 4:
            continue
        sha, author, ts, message = parts
        files = [ln.strip() for ln in files_blob.splitlines() if ln.strip()]
        commits.append({
            "sha": sha.strip(),
            "author": author,
            "ts": int(ts) if ts.isdigit() else 0,
            "message": message.strip("\n"),
            "files": files,
        })
    return commits


def issues_summary(repo: Path, window_days: int) -> dict[str, int] | None:
    """Use `gh issue list` to count open + recently closed issues.

    Returns None if `gh` is missing or fails (caller falls back to neutral).
    """
    try:
        open_out = subprocess.run(
            ["gh", "issue", "list", "--state", "open", "--limit", "500",
             "--json", "number"],
            cwd=repo, check=True, capture_output=True, text=True,
        )
        closed_out = subprocess.run(
            ["gh", "issue", "list", "--state", "closed", "--limit", "500",
             "--search", f"closed:>={_iso_days_ago(window_days)}",
             "--json", "number"],
            cwd=repo, check=True, capture_output=True, text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    import json
    try:
        n_open = len(json.loads(open_out.stdout))
        n_closed = len(json.loads(closed_out.stdout))
    except (ValueError, TypeError):
        return None
    return {"open": n_open, "closed": n_closed}


def _iso_days_ago(days: int) -> str:
    """ISO date `days` ago, format YYYY-MM-DD."""
    from datetime import datetime, timedelta, timezone
    d = datetime.now(timezone.utc) - timedelta(days=days)
    return d.strftime("%Y-%m-%d")
