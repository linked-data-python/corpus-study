"""Build the version-controlled repository manifest from discovery output.

Selection = discovery candidates
           -> GitHub metadata (licence, languages, size, dates, head commit),
              read from ``manifest/repo_stats.jsonl`` when available and from
              the API otherwise
           -> apply the stage-1 criteria of ``[selection]`` (rdfeval.criteria)
           -> pin the head commit of the default branch
           -> write ``manifest/repositories.jsonl``.

The manifest is the reproducibility anchor: repository URL, pinned commit,
licence, discovery strategies, and (after ``analyze``) the RDF-usage counts.
Every candidate rejected by a criterion is written to
``manifest/excluded.jsonl`` with the list of reasons, so the selection is
auditable candidate by candidate rather than only in aggregate.

Selection is **additive**: a repository already in the manifest stays there
even if it no longer satisfies the current criteria — the translations and
pairs already reviewed depend on it. Each record carries ``wave`` (which pass
selected it) and ``selection_ok`` (does it satisfy the *current* criteria), so
the census can be computed on the criteria-conforming stratum alone.
"""

from __future__ import annotations

import json
import time

from .config import MANIFEST_DIR
from .criteria import stage1_reasons
from .discover import _gh_api, load_discovery

MANIFEST_PATH = MANIFEST_DIR / "repositories.jsonl"
EXCLUDED_PATH = MANIFEST_DIR / "excluded.jsonl"
STATS_PATH = MANIFEST_DIR / "repo_stats.jsonl"

# Fields copied from the metadata cache into a manifest record.
METADATA_FIELDS = ("description", "stars", "forks", "fork", "archived", "mirror",
                   "template", "empty", "size_kb", "created_at", "pushed_at",
                   "licence", "primary_language", "languages", "topics",
                   "commits", "last_commit", "default_branch", "unavailable")


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


def load_stats() -> dict[str, dict]:
    """GitHub metadata cache, keyed by the name it was queried under.

    Produced by ``scripts/fetch_repo_stats.py``. Absent cache is not an error:
    selection then falls back to one API call per candidate.
    """
    if not STATS_PATH.exists():
        return {}
    out = {}
    for line in STATS_PATH.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            out[rec["full_name"].lower()] = rec
    return out


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


def _merge(rec: dict, stats: dict[str, dict]) -> dict:
    """Discovery record + cached GitHub metadata, under the canonical name."""
    st = stats.get(rec["full_name"].lower())
    if not st:
        return dict(rec)
    merged = dict(rec)
    merged.update({k: st[k] for k in METADATA_FIELDS if k in st})
    if st.get("canonical"):
        merged["full_name"] = st["canonical"]
        merged["url"] = "https://github.com/" + st["canonical"]
    if st.get("head_commit"):
        merged["head_commit"] = st["head_commit"]
    return merged


def candidates(stats: dict[str, dict] | None = None) -> list[dict]:
    """Every distinct candidate, with its metadata, deduplicated on renames."""
    stats = load_stats() if stats is None else stats
    merged = [_merge(rec, stats) for rec in load_discovery()]
    by_name: dict[str, dict] = {}
    for rec in merged:
        key = rec["full_name"].lower()
        prev = by_name.get(key)
        if prev is None:
            by_name[key] = rec
        else:                            # a rename collided with its new name
            prev["strategies"] = sorted(set(prev.get("strategies", []))
                                        | set(rec.get("strategies", [])))
    return list(by_name.values())


def run(config: dict, limit: int | None = None) -> None:
    cfg = config["selection"]
    stats = load_stats()
    cands = candidates(stats)
    if not cands:
        raise SystemExit("no discovery output; run `rdfeval discover` first")

    prior = {r["full_name"].lower(): r for r in load_manifest()}
    wave = 1 + max([r.get("wave", 1) for r in prior.values()], default=0) \
        if prior else 1
    selected: list[dict] = list(prior.values())
    excluded: list[dict] = []
    max_repos = limit or cfg["max_repos"]

    # Repositories already in the manifest stay, but their conformity to the
    # *current* criteria is recomputed and recorded.
    for rec in selected:
        merged = _merge(rec, stats)
        reasons = stage1_reasons(merged, cfg)
        rec["selection_ok"] = not reasons
        rec["selection_reasons"] = reasons
        rec.setdefault("wave", 1)

    # Rank: seeds first (curated diversity), then number of distinct discovery
    # strategies (cross-confirmed), then stars.  The cap is a safety net, not a
    # selection criterion: with B7 the criteria are meant to do the cutting.
    def rank(rec: dict) -> tuple:
        return ("seed_list" not in rec.get("strategies", []),
                -len(rec.get("strategies", [])),
                -(rec.get("stars") or 0))

    n_api = 0
    for rec in sorted(cands, key=rank):
        if rec["full_name"].lower() in prior:
            continue
        if len(selected) >= max_repos:
            excluded.append({"full_name": rec["full_name"], "url": rec.get("url"),
                             "strategies": rec.get("strategies", []),
                             "excluded_reason": "cap_reached"})
            continue
        full = rec
        if rec.get("commits") is None and rec.get("partial", False):
            full = _complete_metadata(rec) or {}
            n_api += 1
            time.sleep(0.2)
            if not full:
                excluded.append({**rec, "excluded_reason": "metadata_unavailable"})
                continue
        reasons = stage1_reasons(full, cfg)
        if reasons:
            excluded.append({"full_name": full["full_name"], "url": full.get("url"),
                             "description": full.get("description"),
                             "strategies": full.get("strategies", []),
                             "stars": full.get("stars"), "licence": full.get("licence"),
                             "excluded_reason": ",".join(reasons)})
            continue
        sha = full.get("head_commit") or _pin_commit(full)
        if sha is None:
            excluded.append({**{k: full.get(k) for k in ("full_name", "url")},
                             "excluded_reason": "commit_unresolvable"})
            continue
        record = {k: v for k, v in full.items() if k != "head_commit"}
        record["commit"] = sha
        record["snippet_ok"] = (full.get("licence") or "NOASSERTION") in cfg["snippet_licences"]
        record["wave"] = wave
        record["selection_ok"] = True
        record["selection_reasons"] = []
        selected.append(record)
        prior[record["full_name"].lower()] = record

    save_manifest(selected)
    with open(EXCLUDED_PATH, "w") as f:
        for rec in excluded:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    conforming = sum(1 for r in selected if r.get("selection_ok"))
    print(f"manifest: {len(selected)} repositories "
          f"({conforming} satisfy the current criteria, "
          f"{sum(1 for r in selected if r.get('snippet_ok'))} snippet-redistributable), "
          f"{len(excluded)} candidates excluded"
          + (f", {n_api} API calls" if n_api else ""))
