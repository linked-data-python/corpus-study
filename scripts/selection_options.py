"""Test repository selection/exclusion criteria on the 1 188 discovered candidates.

Every criterion here is evaluable *before cloning*, from `manifest/discovery.jsonl`
(which channel found the repository) and `manifest/repo_stats.jsonl` (GitHub
metadata: licence, languages, size, dates, commits, topics). The point is to see
how many repositories each combination would keep, so that the corpus can be
enlarged deliberately instead of by raising `max_repos` blindly.

Two criteria that matter cannot be tested here — they need the clone and the AST
analysis: "at least one RDF-relevant Python file" and "no vendored copy of a
third-party library". They are a second stage, applied after `analyze`.

Usage: python scripts/selection_options.py [--markdown]
"""

from __future__ import annotations

import collections
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNIPPET_LICENCES = {
    "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC",
    "CC0-1.0", "Unlicense", "0BSD", "MPL-2.0",
    "EPL-2.0", "GPL-3.0", "GPL-2.0", "LGPL-3.0", "LGPL-2.1", "AGPL-3.0",
    "EUPL-1.2", "CC-BY-4.0", "CC-BY-SA-4.0", "W3C-20150513",
}
# Course/teaching material: matched on name, description and topics.
TEACHING = ("curso", "course", "tutorial", "exercise", "exercice", "homework",
            "practica", "práctica", "assignment", "workshop", "bootcamp",
            "lecture", "teaching", "student", "classroom", "vorlesung",
            "ejercicio", "tp-", "-tp", "coursework", "kurs")
# Names that are the RDF library itself rather than a user of it.
LIBRARY_CLONES = ("rdflib", "rdfextras", "sparqlwrapper", "isodate")


def _jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def load() -> list[dict]:
    """One record per distinct candidate: discovery channels + GitHub metadata."""
    stats = {r["full_name"].lower(): r for r in _jsonl(ROOT / "manifest" / "repo_stats.jsonl")}
    out = []
    for rec in _jsonl(ROOT / "manifest" / "discovery.jsonl"):
        st = stats.get(rec["full_name"].lower(), {})
        merged = {**rec, **{k: v for k, v in st.items() if k != "full_name"}}
        if st.get("canonical"):
            merged["full_name"] = st["canonical"]   # follow upstream renames
        out.append(merged)
    seen: dict[str, dict] = {}
    for r in out:                        # a rename can collide with its new name
        key = r["full_name"].lower()
        if key not in seen or len(r.get("strategies", [])) > len(seen[key].get("strategies", [])):
            seen[key] = r
    return list(seen.values())


# --- atomic criteria --------------------------------------------------------

def alive(r):        return not r.get("unavailable") and not r.get("empty")
def not_fork(r):     return not r.get("fork")
def not_archived(r): return not r.get("archived")
def not_mirror(r):   return not r.get("mirror") and not r.get("template")


def python_bytes(r) -> int:
    return (r.get("languages") or {}).get("Python", 0)


def python_share(r) -> float:
    langs = r.get("languages") or {}
    total = sum(langs.values())
    return python_bytes(r) / total if total else 0.0


def has_python(r):        return python_bytes(r) > 0
def python_main(r):       return r.get("primary_language") == "Python"
def python_heavy(r):      return python_share(r) >= 0.5
def python_10k(r):        return python_bytes(r) >= 10_000       # ≈ 250 lines
def licenced(r):          return bool(r.get("licence")) and r["licence"] != "NOASSERTION"
def snippet_ok(r):        return (r.get("licence") or "") in SNIPPET_LICENCES
def cross_confirmed(r):   return len(r.get("strategies", [])) >= 2
def on_pypi(r):           return bool(r.get("pypi_name"))
def commits(r):           return r.get("commits") or 0
def stars(r):             return r.get("stars") or 0
def size_kb(r):           return r.get("size_kb") or 0
def last(r):              return (r.get("last_commit") or "")[:10]


def _text(r) -> str:
    return " ".join([r["full_name"], r.get("description") or "",
                     " ".join(r.get("topics") or [])]).lower()


def not_teaching(r):
    return not any(w in _text(r) for w in TEACHING)


def not_library_clone(r):
    name = r["full_name"].split("/", 1)[1].lower()
    return name not in LIBRARY_CLONES


def sane_size(r):
    """Between a toy and a data dump (GitHub diskUsage, in KB)."""
    return 50 <= size_kb(r) <= 200_000


RDF_WORDS = ("rdf", "sparql", "ontolog", "semantic-web", "semantic web",
             "linked-data", "linked data", "knowledge-graph", "knowledge graph",
             "owl", "shacl", "turtle", "triplestore", "skos", "wikidata")


def rdf_signal(r):
    """The project says, in its own words, that it is about RDF."""
    return any(w in _text(r) for w in RDF_WORDS)


def cap_per_org(rows: list[dict], cap: int) -> list[dict]:
    """Keep at most `cap` repositories per GitHub organisation (largest first)."""
    kept, seen = [], {}
    for r in sorted(rows, key=lambda x: (-(x.get("stars") or 0), x["full_name"])):
        org = r["full_name"].split("/")[0].lower()
        if seen.get(org, 0) >= cap:
            continue
        seen[org] = seen.get(org, 0) + 1
        kept.append(r)
    return kept


BASE = [alive, not_fork, not_archived, not_mirror, has_python]


def combo(*preds):
    def f(r):
        return all(p(r) for p in preds)
    return f


C10 = lambda r: commits(r) >= 10        # noqa: E731
C50 = lambda r: commits(r) >= 50        # noqa: E731
A2020 = lambda r: last(r) >= "2020-01-01"   # noqa: E731
A2023 = lambda r: last(r) >= "2023-01-01"   # noqa: E731
S1 = lambda r: stars(r) >= 1            # noqa: E731

B1 = BASE + [python_10k]
B2 = B1 + [C10]
B3 = B2 + [sane_size]
B4 = B3 + [not_teaching, not_library_clone]

OPTIONS: list[tuple[str, str, object]] = [
    ("B0 socle",
     "accessible, non fork, non archivé/miroir/gabarit/vide, ≥ 1 octet de Python",
     combo(*BASE)),
    ("B1 Python substantiel",
     "B0 + ≥ 10 ko de Python (≈ 250 lignes)",
     combo(*B1)),
    ("B2 dépôt suivi",
     "B1 + ≥ 10 commits",
     combo(*B2)),
    ("B3 taille raisonnable",
     "B2 + 50 ko ≤ taille ≤ 200 Mo (ni jouet, ni entrepôt de données)",
     combo(*B3)),
    ("B4 ni cours ni bibliothèque recopiée",
     "B3 + exclusion du matériel pédagogique et des dépôts nommés comme la bibliothèque",
     combo(*B4)),
    ("B5 licence déclarée",
     "B4 + une licence SPDX explicite",
     combo(*B4, licenced)),
    ("B6 licence extractible",
     "B4 + licence autorisant la republication d'extraits (`snippet_licences`)",
     combo(*B4, snippet_ok)),
    ("B7 vivant depuis 2020",
     "B6 + dernier commit ≥ 2020-01-01",
     combo(*B4, snippet_ok, A2020)),
    ("B8 Python majoritaire",
     "B7 + Python ≥ 50 % des octets du dépôt",
     combo(*B4, snippet_ok, A2020, python_heavy)),
    ("B9 projet établi",
     "B8 + ≥ 50 commits",
     combo(*B4, snippet_ok, A2020, python_heavy, C50)),
    ("B10 vu par quelqu'un",
     "B9 + ≥ 1 étoile",
     combo(*B4, snippet_ok, A2020, python_heavy, C50, S1)),
    ("B11 actif depuis 2023",
     "B10 + dernier commit ≥ 2023-01-01",
     combo(*B4, snippet_ok, A2020, python_heavy, C50, S1, A2023)),
    ("A1 attesté par 2 canaux",
     "B4 + trouvé par ≥ 2 canaux de découverte indépendants",
     combo(*B4, cross_confirmed)),
    ("A2 dépendance rdflib déclarée",
     "B4 + distribution PyPI déclarant rdflib (canal Wheelodex)",
     combo(*B4, on_pypi)),
    ("A3 RDF assumé, 2 par organisation",
     "B4 + licence extractible + le projet se décrit comme RDF + plafond de 2 dépôts par organisation",
     (combo(*B4, snippet_ok, rdf_signal), 2)),
]


def describe(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0, "snippet": 0, "stars_med": 0, "commits_med": 0,
                "size_gb": 0.0, "already": 0, "pct2023": 0.0,
                "orgs": 0, "maxorg": 0, "rdf": 0}
    return {
        "n": len(rows),
        "snippet": sum(1 for r in rows if snippet_ok(r)),
        "stars_med": statistics.median([stars(r) for r in rows]),
        "commits_med": statistics.median([commits(r) for r in rows]),
        "size_gb": sum(size_kb(r) for r in rows) / 1_000_000,
        "already": sum(1 for r in rows if r["full_name"] in CURRENT),
        "pct2023": 100 * sum(1 for r in rows if last(r) >= "2023-01-01") / len(rows),
        "orgs": len({r["full_name"].split("/")[0].lower() for r in rows}),
        "maxorg": max(collections.Counter(
            r["full_name"].split("/")[0].lower() for r in rows).values()),
        "rdf": sum(1 for r in rows if rdf_signal(r)),
    }


CURRENT = {r["full_name"] for r in _jsonl(ROOT / "manifest" / "repositories.jsonl")}

if __name__ == "__main__":
    cands = load()
    print(f"{len(cands)} candidats distincts\n")
    results = []
    for name, desc, pred in OPTIONS:
        cap = None
        if isinstance(pred, tuple):
            pred, cap = pred
        rows = [r for r in cands if pred(r)]
        if cap:
            rows = cap_per_org(rows, cap)
        results.append((name, desc, describe(rows), rows))
    results.sort(key=lambda t: -t[2].get("n", 0))
    if "--markdown" in sys.argv:
        print("| option | critères | dépôts | extractibles | se disent RDF | ★ méd. | commits méd. | actif ≥ 2023 | orgs (max) | disque | des 60 |")
        print("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for name, desc, d, _ in results:
            print(f"| **{name}** | {desc} | **{d['n']}** | {d['snippet']} | {d['rdf']} | {d['stars_med']:.0f} | "
                  f"{d['commits_med']:.0f} | {d['pct2023']:.0f} % | {d['orgs']} ({d['maxorg']}) | "
                  f"{d['size_gb']:.1f} Go | {d['already']}/60 |")
    else:
        for name, desc, d, _ in results:
            print(f"{name:34s} n={d['n']:5d}  extr={d['snippet']:5d}  rdf={d['rdf']:5d}  "
                  f"★méd={d['stars_med']:5.0f}  cmt méd={d['commits_med']:6.0f}  "
                  f"≥2023={d['pct2023']:3.0f}%  orgs={d['orgs']:4d}({d['maxorg']:2d})  "
                  f"{d['size_gb']:6.1f} Go  actuels={d['already']:2d}/60")
