# Context shim (see meta.json): subset of scripts/ontology_gate.py from
# synaptixs/ontomesh@f771c8c4ee, so the region executes outside the module.
# Identical bindings for both representations.
import csv
import glob
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import rdflib

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

_DERIVED_MARKERS = ("inferred", "materialised", "materialized")


def _is_derived(path: str) -> bool:
    base = os.path.basename(path).lower()
    return any(m in base for m in _DERIVED_MARKERS)


def _nested_run_dirs(output_dir: str) -> List[str]:
    nested = []
    try:
        for entry in sorted(os.listdir(output_dir)):
            candidate = os.path.join(output_dir, entry)
            if os.path.isdir(candidate) and os.path.isdir(
                os.path.join(candidate, "ontology")
            ):
                nested.append(os.path.abspath(candidate))
    except OSError:
        pass
    return nested


def _turtle_files(output_dir: str) -> List[str]:
    excluded = tuple(d + os.sep for d in _nested_run_dirs(output_dir))
    found = glob.glob(os.path.join(output_dir, "**", "*.ttl"), recursive=True)
    return sorted(
        p for p in found
        if not os.path.abspath(p).startswith(excluded)
    )


def _parse_all(paths: List[str]) -> Tuple[Dict[str, rdflib.Graph], List[Tuple[str, str]]]:
    graphs: Dict[str, rdflib.Graph] = {}
    failures: List[Tuple[str, str]] = []
    for p in paths:
        try:
            g = rdflib.Graph()
            g.parse(p, format="turtle")
            graphs[p] = g
        except Exception as exc:
            first_line = str(exc).splitlines()[0] if str(exc).splitlines() else str(exc)
            failures.append((os.path.relpath(p, REPO_ROOT), first_line[:160]))
    return graphs, failures


def _authored_graph(graphs: Dict[str, rdflib.Graph]) -> rdflib.Graph:
    merged = rdflib.Graph()
    for path, g in graphs.items():
        if _is_derived(path):
            continue
        for triple in g:
            merged.add(triple)
    return merged


def _multi_domain(graph: rdflib.Graph) -> Tuple[int, int]:
    domains: Dict[Any, set] = defaultdict(set)
    for s, _, o in graph.triples((None, rdflib.RDFS.domain, None)):
        domains[s].add(o)
    multi = {k: v for k, v in domains.items() if len(v) > 1}
    worst = max((len(v) for v in multi.values()), default=0)
    return len(multi), worst


def _alignment_unbound(graphs: Dict[str, rdflib.Graph]) -> int:
    align_paths = [p for p in graphs if os.path.basename(p) == "alignment.ttl"]
    if not align_paths:
        return 0
    known = set()
    for path, g in graphs.items():
        if os.path.basename(path) == "alignment.ttl" or _is_derived(path):
            continue
        known |= set(g.subjects())
    unbound = 0
    for path in align_paths:
        g = graphs[path]
        own = set(g.subjects(rdflib.RDF.type, rdflib.OWL.Ontology))
        subjects = {s for s in g.subjects()
                    if isinstance(s, rdflib.URIRef) and s not in own}
        unbound += len([s for s in subjects if s not in known])
    return unbound


def _malformed_iris(graph: rdflib.Graph) -> int:
    bad = set()
    known_schemes = ("http", "https", "urn", "file", "mailto", "doi", "ftp")
    for node in set(graph.all_nodes()) | set(graph.predicates()):
        if not isinstance(node, rdflib.URIRef):
            continue
        text = str(node)
        if any(ch.isspace() for ch in text):
            bad.add(text)
            continue
        scheme, sep, rest = text.partition(":")
        if sep and not rest.startswith("//") and scheme.lower() not in known_schemes:
            bad.add(text)
    return len(bad)


def _count_predicate_objects(graph: rdflib.Graph, predicate, obj) -> int:
    return sum(1 for _ in graph.triples((None, predicate, obj)))


def _cq_rows(output_dir: str) -> Tuple[int, int, int]:
    csv_path = os.path.join(output_dir, "reports", "sparql_cq_test_results.csv")
    if not os.path.isfile(csv_path):
        return (None, None, 0)
    with open(csv_path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return (None, None, 0)
    returning = sum(1 for r in rows if (r.get("row_count") or "0").strip() not in ("0", ""))
    failing = sum(1 for r in rows if (r.get("status") or "").strip() in ("FAIL", "ERROR"))
    return returning, failing, len(rows)


def _pitfall_counts(output_dir: str) -> Tuple[Optional[int], Optional[int]]:
    path = os.path.join(output_dir, "reports", "ontology_quality.csv")
    if not os.path.isfile(path):
        return (None, None)
    firing = critical = 0
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if row.get("kind") != "pitfall":
                continue
            try:
                count = int(row.get("count") or 0)
            except ValueError:
                continue
            if count:
                firing += 1
                if (row.get("severity") or "").strip() == "CRITICAL":
                    critical += 1
    return (firing, critical)
