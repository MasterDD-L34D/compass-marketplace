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
            ["git", *args], cwd=cwd, check=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
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
    """`gh issue list` count of open + closed-in-window. None if `gh` missing/fails."""
    import json
    from datetime import datetime, timedelta, timezone
    since = (datetime.now(timezone.utc) - timedelta(days=window_days)).strftime("%Y-%m-%d")
    base = ["gh", "issue", "list", "--limit", "500", "--json", "number"]
    kw = dict(cwd=repo, check=True, capture_output=True, text=True,
              encoding="utf-8", errors="replace")
    try:
        op = subprocess.run([*base, "--state", "open"], **kw)
        cl = subprocess.run([*base, "--state", "closed", "--search", f"closed:>={since}"], **kw)
        return {"open": len(json.loads(op.stdout)), "closed": len(json.loads(cl.stdout))}
    except (FileNotFoundError, subprocess.CalledProcessError, ValueError, TypeError):
        return None
