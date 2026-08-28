"""Clone every manifest repository at its pinned commit.

Clones are shallow but fetched at the exact recorded SHA, so the working tree
is byte-identical to the manifest state regardless of upstream history
rewrites.  Cloning runs on a thread pool (``[acquisition] jobs``): the work is
network-bound and a few hundred repositories take too long one at a time.  Checkouts live under ``corpus/repos/<owner>__<name>`` (gitignored:
corpus code is never committed to this repository — the manifest suffices to
re-acquire it).
"""

from __future__ import annotations

import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from .config import ROOT
from .select import load_manifest, save_manifest


def repo_dir(config: dict, full_name: str) -> Path:
    return ROOT / config["acquisition"]["corpus_dir"] / full_name.replace("/", "__")


def _acquire_one(rec: dict, dest: Path) -> str | None:
    """Fetch rec['commit'] into dest; returns an error string or None."""
    url = rec["url"] + ".git"
    sha = rec["commit"]
    if (dest / ".git").exists():
        head = subprocess.run(["git", "-C", str(dest), "rev-parse", "HEAD"],
                              capture_output=True, text=True).stdout.strip()
        if head == sha:
            return None
    dest.mkdir(parents=True, exist_ok=True)
    steps = [
        ["git", "init", "-q"],
        ["git", "remote", "add", "origin", url],
        ["git", "fetch", "-q", "--depth", "1", "origin", sha],
        ["git", "checkout", "-q", "FETCH_HEAD"],
    ]
    for cmd in steps:
        r = subprocess.run(cmd, cwd=dest, capture_output=True, text=True)
        if r.returncode != 0 and "remote add" not in " ".join(cmd):
            return f"{' '.join(cmd[:3])}: {r.stderr.strip()[:200]}"
    return None


def run(config: dict) -> None:
    manifest = load_manifest()
    if not manifest:
        raise SystemExit("empty manifest; run `rdfeval select` first")
    jobs = config["acquisition"].get("jobs", 1)
    failures = 0
    done = 0

    def work(rec: dict) -> tuple[dict, str | None]:
        return rec, _acquire_one(rec, repo_dir(config, rec["full_name"]))

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for rec, err in pool.map(work, manifest):
            done += 1
            if err:
                failures += 1
                rec["acquire_error"] = err
                print(f"  ! [{done}/{len(manifest)}] {rec['full_name']}: {err}",
                      flush=True)
            else:
                rec.pop("acquire_error", None)
                print(f"  ✓ [{done}/{len(manifest)}] {rec['full_name']} "
                      f"@ {rec['commit'][:10]}", flush=True)
    save_manifest(manifest)
    print(f"acquire: {len(manifest) - failures}/{len(manifest)} repositories ready")
    if failures:
        raise SystemExit(f"{failures} acquisition failure(s) — recorded in the manifest")
