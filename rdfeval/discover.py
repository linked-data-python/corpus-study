"""Repository discovery: GitHub search, Wheelodex reverse-dependencies, seeds.

Every candidate repository is written to ``manifest/discovery.jsonl`` with the
strategy (or strategies) that surfaced it.  Discovery is additive and
re-runnable; hits are merged on the repository's full name.

Network access: the GitHub queries go through the authenticated ``gh`` CLI;
Wheelodex and PyPI are public JSON APIs.
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from collections import defaultdict

from .config import MANIFEST_DIR

DISCOVERY_PATH = MANIFEST_DIR / "discovery.jsonl"

USER_AGENT = "ldpy-corpus-eval/0.1 (research; contact: maxime.lefrancois@emse.fr)"


def _gh_api(path: str) -> dict | list:
    result = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh api {path}: {result.stderr.strip()[:200]}")
    return json.loads(result.stdout)


def _http_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _repo_record(item: dict, strategy: str) -> dict:
    """Normalize a GitHub repository API object."""
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
        "strategies": [strategy],
    }


# --- strategies -------------------------------------------------------------

def github_code_search(queries: list[str], max_pages: int) -> list[dict]:
    hits: dict[str, dict] = {}
    for query in queries:
        for page in range(1, max_pages + 1):
            from urllib.parse import quote
            path = f"search/code?q={quote(query)}&per_page=100&page={page}"
            try:
                data = _gh_api(path)
            except RuntimeError as e:
                print(f"  code search stopped ({e})")
                break
            items = data.get("items", [])
            for it in items:
                repo = it["repository"]
                rec = hits.setdefault(
                    repo["full_name"], _repo_record(repo, "github_code_search"))
                rec.setdefault("query_hits", 0)
                rec["query_hits"] += 1
            if len(items) < 100:
                break
            time.sleep(7)   # code-search secondary rate limit
    # code-search repo objects are partial; flag for metadata completion
    for rec in hits.values():
        rec["partial"] = True
    return list(hits.values())


def github_repo_search(queries: list[str], max_pages: int) -> list[dict]:
    hits: dict[str, dict] = {}
    for query in queries:
        for page in range(1, max_pages + 1):
            from urllib.parse import quote
            path = f"search/repositories?q={quote(query)}&per_page=100&page={page}"
            try:
                data = _gh_api(path)
            except RuntimeError as e:
                print(f"  repo search stopped ({e})")
                break
            items = data.get("items", [])
            for it in items:
                hits.setdefault(it["full_name"],
                                _repo_record(it, "github_repo_search"))
            if len(items) < 100:
                break
            time.sleep(3)
    return list(hits.values())


def wheelodex_rdepends(package: str = "rdflib", max_pages: int = 2) -> list[dict]:
    """PyPI projects depending on rdflib, resolved to GitHub repositories.

    Wheelodex's JSON API was withdrawn; the reverse-dependency listing is
    scraped from the paginated HTML (stable ``/projects/<name>/`` links)."""
    import re as _re
    out: list[str] = []
    for page in range(1, max_pages + 1):
        url = (f"https://www.wheelodex.org/projects/{package}/rdepends/"
               + (f"?page={page}" if page > 1 else ""))
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                html = resp.read().decode("utf-8", "replace")
        except Exception as e:
            print(f"  wheelodex stopped ({e})")
            break
        names = _re.findall(r'href="/projects/([\w.-]+)/"', html)
        new = [n for n in names if n != package and n != ""]
        if not new:
            break
        out.extend(new)
        time.sleep(0.5)
    out = sorted(set(out))
    records = []
    for name in out:
        try:
            meta = _http_json(f"https://pypi.org/pypi/{name}/json")
        except Exception:
            continue
        info = meta.get("info", {})
        urls = info.get("project_urls") or {}
        candidates = [u for u in list(urls.values()) + [info.get("home_page") or ""]
                      if u and "github.com/" in u]
        if not candidates:
            continue
        gh_path = candidates[0].split("github.com/")[1].strip("/")
        parts = gh_path.split("/")
        if len(parts) < 2:
            continue
        full_name = "/".join(parts[:2]).removesuffix(".git")
        records.append({
            "full_name": full_name,
            "url": f"https://github.com/{full_name}",
            "pypi_name": name,
            "strategies": ["wheelodex_rdepends"],
            "partial": True,
        })
        time.sleep(0.1)
    return records


def seed_list(seeds: list[str]) -> list[dict]:
    return [{"full_name": s, "url": f"https://github.com/{s}",
             "strategies": ["seed_list"], "partial": True} for s in seeds]


# --- merge + persist --------------------------------------------------------

def merge(existing: list[dict], new: list[dict]) -> list[dict]:
    by_name: dict[str, dict] = {}
    for rec in existing + new:
        key = rec["full_name"].lower()
        if key in by_name:
            prev = by_name[key]
            prev["strategies"] = sorted(set(prev["strategies"]) | set(rec["strategies"]))
            for k, v in rec.items():
                if k not in ("strategies",) and prev.get(k) in (None, "", 0, True) \
                        and v not in (None, ""):
                    if k == "partial":
                        prev[k] = prev.get("partial", True) and v
                    else:
                        prev.setdefault(k, v)
        else:
            by_name[key] = dict(rec)
    return sorted(by_name.values(), key=lambda r: r["full_name"].lower())


def load_discovery() -> list[dict]:
    if not DISCOVERY_PATH.exists():
        return []
    return [json.loads(line) for line in DISCOVERY_PATH.read_text().splitlines()
            if line.strip()]


def save_discovery(records: list[dict]) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    with open(DISCOVERY_PATH, "w") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run(config: dict) -> None:
    cfg = config["discovery"]
    merged = load_discovery()
    runners = {
        "seed_list": lambda: seed_list(cfg["seed_repositories"]),
        "github_repo_search": lambda: github_repo_search(
            cfg["github_repo_queries"], cfg["max_pages_per_query"]),
        "github_code_search": lambda: github_code_search(
            cfg["github_code_queries"], cfg["max_pages_per_query"]),
        "wheelodex_rdepends": wheelodex_rdepends,
    }
    for strategy in cfg["strategies"]:
        print(f"strategy: {strategy}")
        try:
            found = runners[strategy]()
        except Exception as e:               # a failed channel must not lose the rest
            print(f"  ! strategy {strategy} failed: {e}")
            continue
        merged = merge(merged, found)
        save_discovery(merged)               # incremental: crash-safe
    counts = defaultdict(int)
    for rec in merged:
        for s in rec["strategies"]:
            counts[s] += 1
    print(f"discovery: {len(merged)} candidate repositories "
          f"({', '.join(f'{k}: {v}' for k, v in sorted(counts.items()))})")
