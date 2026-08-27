"""Build the version-controlled repository manifest from discovery output.

Selection = discovery candidates
           -> complete metadata via the GitHub API (licence, fork, size…)
           -> apply the inclusion criteria of [selection] in the config
           -> pin the head commit of the default branch
           -> write ``manifest/repositories.jsonl``.

The manifest is the reproducibility anchor: repository URL, pinned commit,
licence, discovery strategies, and (after ``analyze``) the RDF-usage counts.
Repositories excluded by a criterion are kept in
``manifest/excluded.jsonl`` with the reason, so the selection is auditable.
"""

from __future__ import annotations

import json
import time

from .config import MANIFEST_DIR
from .discover import _gh_api, load_discovery

MANIFEST_PATH = MANIFEST_DIR / "repositories.jsonl"
EXCLUDED_PATH = MANIFEST_DIR / "excluded.jsonl"


def load_manifest() -> list[dict]:
    if not MANIFEST_PATH.exists():
        return []
    return [json.loads(line) for line in MANIFEST_PATH.read_text().splitlines()
            if line.strip()]


def save_manifest(records: list[dict]) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        for rec in sorted(records, key=lambda r: r["full_name"].lower()):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _complete_metadata(rec: dict) -> dict | None:
    """Fetch the full repository object (also resolves renames/redirects)."""
    try:
        item = _gh_api(f"repos/{rec['full_name']}")
    except RuntimeError:
        return None
    return {
        "full_name": item["full_name"],
        "url": item["html_url"],
        "description": (item.get("description") or "")[:300],
        "stars": item.get("stargazers_count", 0),
        "fork": item.get("fork", False),
        "archived": item.get("archived", False),
        "licence": (item.get("license") or {}).get("spdx_id"),
        "default_branch": item.get("default_branch"),
        "size_kb": item.get("size"),
        "pushed_at": item.get("pushed_at"),
        "strategies": rec.get("strategies", []),
        "pypi_name": rec.get("pypi_name"),
        "query_hits": rec.get("query_hits"),
    }


def _pin_commit(rec: dict) -> str | None:
    try:
        data = _gh_api(f"repos/{rec['full_name']}/commits/{rec['default_branch']}")
    except RuntimeError:
        return None
    return data.get("sha")


def run(config: dict, limit: int | None = None) -> None:
    cfg = config["selection"]
    candidates = load_discovery()
    if not candidates:
        raise SystemExit("no discovery output; run `rdfeval discover` first")
    prior = {r["full_name"].lower(): r for r in load_manifest()}
    selected: list[dict] = list(prior.values())
    excluded: list[dict] = []
    max_repos = limit or cfg["max_repos"]

    # Rank candidates: seeds first (curated diversity), then by number of
    # distinct discovery strategies (cross-confirmed), then stars.
    def rank(rec: dict) -> tuple:
        return ("seed_list" not in rec["strategies"],
                -len(rec["strategies"]),
                -(rec.get("stars") or 0))

    for rec in sorted(candidates, key=rank):
        if len(selected) >= max_repos:
            break
        if rec["full_name"].lower() in prior:
            continue
        full = _complete_metadata(rec) if rec.get("partial", False) else dict(rec)
        time.sleep(0.2)
        if full is None:
            excluded.append({**rec, "excluded_reason": "metadata_unavailable"})
            continue
        if full["full_name"].lower() in prior:
            continue    # rename resolved to an already-selected repository
        if cfg["exclude_forks"] and full.get("fork"):
            excluded.append({**full, "excluded_reason": "fork"})
            continue
        if cfg["exclude_archived"] and full.get("archived"):
            excluded.append({**full, "excluded_reason": "archived"})
            continue
        sha = _pin_commit(full)
        if sha is None:
            excluded.append({**full, "excluded_reason": "commit_unresolvable"})
            continue
        full["commit"] = sha
        full["snippet_ok"] = (full.get("licence") or "NOASSERTION") in cfg["snippet_licences"]
        selected.append(full)
        prior[full["full_name"].lower()] = full
        print(f"  + {full['full_name']} @ {sha[:10]} [{full.get('licence')}]")

    save_manifest(selected)
    with open(EXCLUDED_PATH, "w") as f:
        for rec in excluded:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"manifest: {len(selected)} repositories "
          f"({sum(1 for r in selected if r.get('snippet_ok'))} snippet-redistributable), "
          f"{len(excluded)} excluded")
