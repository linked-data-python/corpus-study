"""Validation driver for BBDFrancois__Web_Data_Project_DIA6_Royal_Family__src_m2_kb_construction.py__update_schema_and_sanitize_kb.

This region READS three graphs from files (expanded_kb_file, ontology_file,
alignment_file) and WRITES three more (output_clean_kb_file,
ontology_expanded_file, alignment_expanded_file) — it never holds an
in-memory graph the standard `run_pair(..., fixture="fixture.ttl")` recipe
could hand it as a single argument, and it returns nothing. So this driver
does not use that recipe directly: it stages the three input fixtures
(fixture_kb.nt, fixture_ontology.ttl, fixture_alignment.ttl — read-only,
shared by both runs) and gives each version its own temp directory to write
into, then compares the three output files it produced, one by one, by RDF
isomorphism (design record corpus/405: reading regions are proved by
equality of what they produce from the same input, and a graph a region
produces is still compared by isomorphism, whether it reaches the driver as
a return value or as a file on disk).

The fixture is part of the translation. fixture_kb.nt covers: several
dbpedia properties/entities to newly absorb, one property and one entity
pre-aligned in fixture_alignment.ttl (the "zero new" path), a predicate and
entities reused across two triples (the memoisation path), a noisy literal
(phase 1 purge), and a neighbouring pair with a non-dbpedia predicate and
non-dbr terms that phases 2/3 must leave untouched.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import _exec_ldpy, _exec_python, graphs_isomorphic, _emit

HERE = Path(__file__).resolve().parent


def _make_case():
    work = Path(tempfile.mkdtemp(prefix="update-schema-sanitize-"))
    return {
        "expanded_kb_file": str(HERE / "fixture_kb.nt"),
        "ontology_file": str(HERE / "fixture_ontology.ttl"),
        "alignment_file": str(HERE / "fixture_alignment.ttl"),
        "output_clean_kb_file": str(work / "clean_kb.nt"),
        "ontology_expanded_file": str(work / "ontology_expanded.ttl"),
        "alignment_expanded_file": str(work / "alignment_expanded.ttl"),
    }, work


verdict = {"example": HERE.name, "equivalent": False, "method": "output-files",
           "diffs": [], "error": None}

work_o = work_t = None
try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    fo, ft = ns_o.get("update_schema_and_sanitize_kb"), \
        ns_t.get("update_schema_and_sanitize_kb")
    if not callable(fo) or not callable(ft):
        raise RuntimeError("entry point not found in both modules")

    kwargs_o, work_o = _make_case()
    kwargs_t, work_t = _make_case()
    fo(**kwargs_o)
    ft(**kwargs_t)

    checks = [
        ("clean_kb", kwargs_o["output_clean_kb_file"],
         kwargs_t["output_clean_kb_file"], "nt"),
        ("ontology_expanded", kwargs_o["ontology_expanded_file"],
         kwargs_t["ontology_expanded_file"], "turtle"),
        ("alignment_expanded", kwargs_o["alignment_expanded_file"],
         kwargs_t["alignment_expanded_file"], "turtle"),
    ]
    diffs: list[str] = []
    for label, path_o, path_t, fmt in checks:
        go = Graph().parse(path_o, format=fmt)
        gt = Graph().parse(path_t, format=fmt)
        if not graphs_isomorphic(go, gt):
            diffs.append(f"{label}: graphs not isomorphic "
                         f"({len(go)} vs {len(gt)} triples)")
    if out_o != out_t:
        diffs.append(f"stdout differs ({out_o[:200]!r} vs {out_t[:200]!r})")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)
finally:
    if work_o is not None:
        shutil.rmtree(work_o, ignore_errors=True)
    if work_t is not None:
        shutil.rmtree(work_t, ignore_errors=True)

_emit(verdict)
VERDICT = verdict
