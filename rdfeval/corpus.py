"""Corpus-wide analysis: run the AST analyser over every checkout.

Outputs (machine-readable, one line per file):

    results/raw/analysis/<owner>__<name>.jsonl   per-file metrics
    results/raw/files_index.jsonl                all files, all repositories
    results/summary/corpus.json                  corpus-level roll-up

The manifest is updated in place with ``python_files``, ``rdf_files``
(files with at least one detected RDF operation) and ``rdf_deps`` (RDF-related
distributions found in requirement/config files).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .acquire import repo_dir
from .analyze import analyze_file
from .config import RESULTS_RAW, RESULTS_SUMMARY, provenance
from .criteria import is_vendored, stage2_reason
from .select import load_manifest, save_manifest

ANALYSIS_DIR = RESULTS_RAW / "analysis"
FILES_INDEX = RESULTS_RAW / "files_index.jsonl"

RDF_DISTRIBUTIONS = re.compile(
    r"^\s*\"?(rdflib\b[\w.-]*|sparqlwrapper|owlrl|pyshacl|pyld|prettytable-rdf|"
    r"rdflib-jsonld|oxrdflib|pyoxigraph|rdfpandas|sparql-slurper)",
    re.IGNORECASE | re.MULTILINE)

REQUIREMENT_FILES = ("requirements*.txt", "setup.py", "setup.cfg",
                     "pyproject.toml", "Pipfile", "environment.yml")


def _python_files(root: Path, full_name: str,
                  acfg: dict) -> tuple[list[tuple[Path, str]], int]:
    """Analysable Python files of a checkout, and how many were vendored.

    Two kinds of directory are skipped: those of ``exclude_dirs`` anywhere in
    the path (a committed virtualenv, a build tree), and a top-level tree that
    is a third-party library copied into the repository (``vendored_dirs``) —
    the latter only when it is not the repository's own package.
    """
    exclude_dirs = set(acfg["exclude_dirs"])
    max_bytes = acfg["max_file_bytes"]
    files: list[tuple[Path, str]] = []
    vendored = 0
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root)
        if any(part in exclude_dirs for part in rel.parts):
            continue
        if is_vendored(rel.parts, full_name, acfg):
            vendored += 1
            continue
        try:
            if path.stat().st_size > max_bytes:
                continue
        except OSError:
            continue
        files.append((path, str(rel)))
    return files, vendored


def _rdf_deps(root: Path) -> list[str]:
    found: set[str] = set()
    for pattern in REQUIREMENT_FILES:
        for f in root.glob(pattern):
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in RDF_DISTRIBUTIONS.finditer(text):
                found.add(m.group(1).lower().strip('"'))
    return sorted(found)


def run(config: dict) -> None:
    manifest = load_manifest()
    if not manifest:
        raise SystemExit("empty manifest; run `rdfeval select` first")
    acfg = config["analysis"]
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_SUMMARY.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    for rec in manifest:
        root = repo_dir(config, rec["full_name"])
        if not (root / ".git").exists():
            print(f"  ! {rec['full_name']}: not acquired, skipped")
            continue
        rows = []
        n_err = 0
        files, n_vendored = _python_files(root, rec["full_name"], acfg)
        for path, rel in files:
            fa = analyze_file(path)
            row = fa.to_dict()
            row["path"] = rel
            row["repository"] = rec["full_name"]
            row["commit"] = rec["commit"]
            rows.append(row)
            if fa.error:
                n_err += 1
        out = ANALYSIS_DIR / (rec["full_name"].replace("/", "__") + ".jsonl")
        with open(out, "w") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        rec["python_files"] = len(rows)
        rec["rdf_files"] = sum(1 for r in rows if r["rdf_ops"] > 0)
        rec["analysis_errors"] = n_err
        rec["vendored_files_skipped"] = n_vendored
        rec["rdf_deps"] = _rdf_deps(root)
        all_rows.extend(rows)
        print(f"  {rec['full_name']}: {rec['python_files']} py files, "
              f"{rec['rdf_files']} with RDF ops, {n_err} unparsable"
              + (f", {n_vendored} vendored skipped" if n_vendored else ""))

    # Stage-2 pruning: repositories that satisfied the metadata criteria but
    # turn out to hold no analysable RDF Python.  They stay in the manifest —
    # regions and pairs already reviewed refer to them — but are marked, and
    # excluded from the census, from the surface analysis and from sampling.
    pruned = 0
    if config["selection"].get("prune_after_analysis", True):
        for rec in manifest:
            reason = stage2_reason(rec, config["selection"])
            rec["pruned"] = reason
            pruned += bool(reason)

    save_manifest(manifest)
    with open(FILES_INDEX, "w") as f:
        for row in all_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    kept = {r["full_name"] for r in manifest if not r.get("pruned")}
    conforming = {r["full_name"] for r in manifest
                  if not r.get("pruned") and r.get("selection_ok", True)}
    summary = {
        "provenance": provenance(config),
        "repositories": len(manifest),
        "repositories_analysed": len({r["repository"] for r in all_rows}),
        "repositories_pruned": sum(1 for r in manifest if r.get("pruned")),
        "repositories_conforming": len(conforming),
        "vendored_files_skipped": sum(r.get("vendored_files_skipped", 0)
                                      for r in manifest),
        **_census([r for r in all_rows if r["repository"] in kept]),
        "conforming_stratum": _census(
            [r for r in all_rows if r["repository"] in conforming]),
    }
    with open(RESULTS_SUMMARY / "corpus.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"analyze: {summary['python_files']} files, "
          f"{summary['rdf_files']} RDF-relevant, "
          f"{summary['total_rdf_ops']} RDF operations"
          + (f" ({pruned} repositories pruned)" if pruned else ""))


def _census(rows: list[dict]) -> dict:
    """Corpus-level roll-up over a set of analysed files."""
    rdf_rows = [r for r in rows if r["rdf_ops"] > 0]
    categories: dict[str, int] = {}
    for r in rdf_rows:
        for k, v in r["category_counts"].items():
            categories[k] = categories.get(k, 0) + v
    return {
        "python_files": len(rows),
        "rdf_files": len(rdf_rows),
        "unparsable_files": sum(1 for r in rows if r["error"]),
        "total_rdf_ops": sum(r["rdf_ops"] for r in rdf_rows),
        "certain_ops": sum(r["certain_ops"] for r in rdf_rows),
        "total_triples_added": sum(r["triples_added"] for r in rdf_rows),
        "total_terms_constructed": sum(r["terms_constructed"] for r in rdf_rows),
        "rdf_loc_total": sum(r["total_loc"] for r in rdf_rows),
        "rdf_lines_total": sum(r["rdf_lines"] for r in rdf_rows),
        "category_totals": dict(sorted(categories.items())),
        "density_deciles": _deciles([r["rdf_node_density"] for r in rdf_rows]),
    }


def _deciles(values: list[float]) -> list[float]:
    if not values:
        return []
    vs = sorted(values)
    return [round(vs[min(len(vs) - 1, int(q * len(vs) / 10))], 5)
            for q in range(11)]


def load_files_index() -> list[dict]:
    if not FILES_INDEX.exists():
        raise SystemExit("no files index; run `rdfeval analyze` first")
    return [json.loads(line) for line in FILES_INDEX.read_text().splitlines()
            if line.strip()]
