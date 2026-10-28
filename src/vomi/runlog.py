"""Run manifests (AGENTS.md §8): provenance for every number we report."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import platform
import subprocess
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, timeout=20).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def gpu_snapshot() -> list[dict]:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=20,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    rows = []
    for line in out.strip().splitlines():
        name, driver, total, used = [x.strip() for x in line.split(",")]
        rows.append({"name": name, "driver": driver, "memory_total_mib": int(total), "memory_used_mib": int(used)})
    return rows


def config_hash(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


def new_manifest(kind: str, cfg: dict) -> dict:
    status = _git("status", "--porcelain")
    return {
        "run_id": f"{kind}-{dt.datetime.now().strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}",
        "kind": kind,
        "git_commit": _git("rev-parse", "HEAD") or None,
        "git_dirty": bool(status) if status is not None else None,
        "config": cfg,
        "config_hash": config_hash(cfg),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "started_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "gpu_at_start": gpu_snapshot(),
    }


def finish(manifest: dict, out_dir: Path, **extra) -> Path:
    manifest.update(extra)
    manifest["ended_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, default=str))
    return path
