"""Fetch stars / commit count / last-commit date for every candidate repository.

`manifest/discovery.jsonl` records stars and `pushed_at` as they were at
discovery time, but not the number of commits, and a push date is not a commit
date. This script asks the GitHub GraphQL API for the three figures at once
(50 repositories per request, aliased) and caches them in
``manifest/repo_stats.jsonl`` so that `scripts/export_candidates.py` stays
offline and the CSV stays reproducible.

Recorded per repository: description, stars/forks, fork/archived/mirror/template
/empty flags, licence (SPDX), disk usage, creation and push dates, primary and
per-language byte counts, topics, number of commits on the default branch and
the date and SHA of its head commit, plus the UTC timestamp of the query. The
SHA is what lets `rdfeval select` pin a commit without one API call per
repository. Discovery
records coming from GitHub *code* search are partial (no licence, no size, no
dates); this pass completes every candidate uniformly, which is what makes
`scripts/selection_options.py` able to test selection criteria on all 1 188. ``full_name`` is
always the name the row was *queried under* (the one appearing in the manifests)
so the join stays exact; ``canonical`` holds the name GitHub answers with, which
differs when the project was renamed or transferred.

Usage: python scripts/fetch_repo_stats.py [--refresh]
       (without --refresh, repositories already cached are not re-queried)
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "manifest" / "repo_stats.jsonl"
BATCH = 50
ENDPOINT = "https://api.github.com/graphql"

FRAGMENT = """
  r%(i)d: repository(owner: %(owner)s, name: %(name)s) {
    nameWithOwner
    description
    stargazerCount
    forkCount
    isFork
    isArchived
    isMirror
    isTemplate
    isEmpty
    diskUsage
    createdAt
    pushedAt
    licenseInfo { spdxId }
    primaryLanguage { name }
    languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
      edges { size node { name } }
    }
    repositoryTopics(first: 12) { nodes { topic { name } } }
    defaultBranchRef { name target { ... on Commit { oid committedDate history { totalCount } } } }
  }"""


def _token() -> str:
    out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("gh auth token failed; run `gh auth login`")
    return out.stdout.strip()


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _query(token: str, batch: list[str]) -> dict:
    parts = []
    for i, full_name in enumerate(batch):
        owner, name = full_name.split("/", 1)
        parts.append(FRAGMENT % {"i": i, "owner": json.dumps(owner), "name": json.dumps(name)})
    body = json.dumps({"query": "query {" + "".join(parts) + "\n}"}).encode()
    req = urllib.request.Request(
        ENDPOINT, data=body,
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "ldpy-corpus-eval/0.1 (research)"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:          # 502/secondary rate limit
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


def main() -> None:
    refresh = "--refresh" in sys.argv[1:]
    names: list[str] = []
    seen: set[str] = set()
    for source in ("discovery.jsonl", "repositories.jsonl", "excluded.jsonl"):
        for rec in _jsonl(ROOT / "manifest" / source):
            key = rec["full_name"].lower()
            if key not in seen:
                seen.add(key)
                names.append(rec["full_name"])

    cached = {} if refresh else {r["full_name"].lower(): r for r in _jsonl(CACHE)}
    todo = [n for n in names if n.lower() not in cached]
    print(f"{len(names)} dépôts, {len(cached)} en cache, {len(todo)} à interroger")

    token = _token()
    stamp = datetime.now(timezone.utc).isoformat()
    for start in range(0, len(todo), BATCH):
        batch = todo[start:start + BATCH]
        payload = _query(token, batch)
        data = payload.get("data") or {}
        for i, full_name in enumerate(batch):
            node = data.get(f"r{i}")
            rec = {"full_name": full_name, "canonical": None, "queried_at": stamp,
                   "stars": None, "commits": None, "last_commit": None,
                   "unavailable": node is None}
            if node:
                branch = node.get("defaultBranchRef") or {}
                target = branch.get("target") or {}
                langs = {e["node"]["name"]: e["size"]
                         for e in (node.get("languages") or {}).get("edges", [])}
                rec.update(canonical=node["nameWithOwner"],
                           description=(node.get("description") or "")[:300],
                           stars=node.get("stargazerCount"),
                           forks=node.get("forkCount"),
                           fork=node.get("isFork"),
                           archived=node.get("isArchived"),
                           mirror=node.get("isMirror"),
                           template=node.get("isTemplate"),
                           empty=node.get("isEmpty"),
                           size_kb=node.get("diskUsage"),
                           created_at=node.get("createdAt"),
                           pushed_at=node.get("pushedAt"),
                           licence=(node.get("licenseInfo") or {}).get("spdxId"),
                           primary_language=(node.get("primaryLanguage") or {}).get("name"),
                           languages=langs,
                           topics=[t["topic"]["name"] for t in
                                   (node.get("repositoryTopics") or {}).get("nodes", [])],
                           default_branch=branch.get("name"),
                           head_commit=target.get("oid"),
                           commits=(target.get("history") or {}).get("totalCount"),
                           last_commit=target.get("committedDate"))
            cached[full_name.lower()] = rec
        print(f"  {min(start + BATCH, len(todo))}/{len(todo)}", flush=True)
        time.sleep(0.5)

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as f:
        for rec in sorted(cached.values(), key=lambda r: r["full_name"].lower()):
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    missing = sum(1 for r in cached.values() if r.get("unavailable"))
    print(f"{CACHE.relative_to(ROOT)}: {len(cached)} dépôts ({missing} inaccessibles)")


if __name__ == "__main__":
    main()
