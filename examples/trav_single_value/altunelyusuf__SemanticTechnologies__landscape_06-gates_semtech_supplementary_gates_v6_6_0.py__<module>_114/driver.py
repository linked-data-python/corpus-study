"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_06-gates_semtech_supplementary_gates_v6_6_0.py__<module>_114.

The region is a block of module-level code that parses six graphs from
`{HERE}/…` and reads them: `tb.value(...)` twice per taxonomy node (G2),
`tb.subject_objects(p)` per relation property (G3), and, for each graph, the
owl:Ontology subject and its header values (`g.subjects`, `g.value` x3).

Why a plain module-state comparison would be hollow here: the excerpt keeps
only the lines that touch RDF, so `bad` is re-assigned several times and
only the last value (the header gate) survives in the module globals; what
G2 and G3 read leaves no trace except in `edges` and `sem_classes`.  So the
driver makes the READS visible: `rdflib.Graph.triples` is wrapped, in the
driver process BEFORE the two sides fork from it, so that each side prints
every pattern asked of a graph and every triple yielded.  Both sides read
through `Graph.triples` (`g.value`/`g.subjects`/`g.subject_objects` do, and so
does the `m{ }` island), so the printed stream is part of the compared
stdout: a wrong subject, predicate, graph or number of values consumed shows.

Inputs.  The files the region parses are small stand-ins in this directory
(see meta.json).  The driver runs the pair once per INPUT, each in its own
scratch copy of the example directory with some of the TTL files replaced,
and merges the verdicts into one (a single scenario that differs makes the
pair differ):
  shipped      the stand-ins as shipped: tbox with a wrong sectionNumber, an
               empty classCode, a missing classCode/sectionNumber, two
               classCode values, a typed-integer sectionNumber, an edge to a
               non-class, a neighbour predicate outside REL_PROPS, a header
               without dcterms:rights and with an empty dcterms:modified;
               abox with TWO owl:Ontology, shacl with none, document with a
               stale versionInfo/versionIRI and a zero dcterms:created, page
               with two versionInfo values, research with a non-Ontology
               neighbour that carries versionInfo.
  clean        every header complete and every class right: no gate fails
  empty        every graph empty: each `g.value` is None, onts=0 everywhere
  multi-first  the two classCode values of T1C1 in the other order: the
               first value read is what counts
  falsy        header values that are present but falsy (""/0/false) next to
               a "6.6.0" versionInfo
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

import rdflib

from rdfeval.harness import _emit, run_pair

EX_DIR = Path(__file__).resolve().parent


# --- make the reads visible --------------------------------------------------
_orig_triples = rdflib.Graph.triples


def _show(t):
    return " ".join("*" if x is None else x.n3() for x in t)


def _logged_triples(self, triple):
    print("ask", _show(triple))
    for t in _orig_triples(self, triple):
        print("got", _show(t))
        yield t


rdflib.Graph.triples = _logged_triples


# --- the inputs --------------------------------------------------------------
PRE = """\
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix semtech: <http://example.org/semtech#> .
"""

HEADER = {
    "rdfs:label": '"label"@en',
    "dcterms:license": "<https://creativecommons.org/licenses/by/4.0/>",
    "dcterms:rights": '"CC BY 4.0"',
    "dcterms:rightsHolder": '"holder"',
    "dcterms:publisher": '"publisher"',
    "dcterms:creator": '"creator"',
    "dcterms:created": '"2026-08-04"^^xsd:date',
    "dcterms:modified": '"2026-08-28"^^xsd:date',
    "dcterms:identifier": '"id"',
    "owl:versionInfo": '"6.6.0"',
    "owl:versionIRI": "<http://example.org/semtech/x/6.6.0>",
}


def header(**override):
    h = {**HEADER, **override}
    body = " ;\n    ".join(f"{p} {v}" for p, v in h.items())
    return f"<http://example.org/semtech/x> a owl:Ontology ;\n    {body} .\n"


CL = {"T1": "T1_SemanticTechnologyFoundations", "T1C1": "T1C1_KnowledgeRepresentationModels",
      "T1C2": "T1C2_OntologyandSchemaLanguages", "T2": "T2_StandardsChapter",
      "T2C1": "T2C1_W3CStandards", "T3": "T3_Ecosystem"}
CODES = {"T1": "1", "T1C1": "1.1", "T1C2": "1.2", "T2": "2", "T2C1": "2.1", "T3": "3"}
CLEAN_TBOX = PRE + header() + "".join(
    f'semtech:{CL[k]} a owl:Class ; semtech:classCode "{k}" ; semtech:sectionNumber "{CODES[k]}" .\n'
    for k in CL) + f"""\
semtech:{CL['T1C2']} semtech:buildsOn semtech:{CL['T1C1']} .
semtech:{CL['T1C1']} semtech:standardizedBy semtech:{CL['T2C1']} .
semtech:{CL['T1']} semtech:informs semtech:{CL['T3']} .
"""

SHIPPED_TBOX = (EX_DIR / "02-ontology" / "semtech_tbox_v6_6_0.ttl").read_text()

TTLS = {
    "research": "01-research/semtech_research_v6_6_0.ttl",
    "tbox": "02-ontology/semtech_tbox_v6_6_0.ttl",
    "abox": "02-ontology/semtech_abox_v6_6_0.ttl",
    "shacl": "02-ontology/semtech_shacl_v6_6_0.ttl",
    "document": "03-document/semtech_document_v6_6_0.ttl",
    "page": "04-page/semtech_page_abox_v6_6_0.ttl",
}

FALSY = {
    "research": PRE + header(**{"dcterms:license": '""', "dcterms:created": "0",
                                "dcterms:modified": "false"}),
    "tbox": CLEAN_TBOX,
    "abox": PRE + header(**{"owl:versionIRI": '""'}),
    "shacl": PRE + header(**{"owl:versionInfo": "6.6"}),
    "document": PRE + header(**{"dcterms:rights": '""', "dcterms:identifier": "0"}),
    "page": PRE + header(**{"owl:versionIRI": '"6.6.0"'}),
}

SCENARIOS = {
    "clean": {k: (CLEAN_TBOX if k == "tbox" else PRE + header()) for k in TTLS},
    "empty": {k: "" for k in TTLS},
    "multi-first": {"tbox": SHIPPED_TBOX.replace('"T1C1", "ALT-CODE"', '"ALT-CODE", "T1C1"')},
    "falsy": FALSY,
}


def _verdict_of(stderr_text: str) -> dict:
    for line in stderr_text.splitlines():
        if line.startswith("RDFEVAL-VERDICT "):
            return json.loads(line[len("RDFEVAL-VERDICT "):])
    raise RuntimeError("run_pair printed no verdict: " + stderr_text[-500:])


def _run(driver_file: Path) -> dict:
    buf = io.StringIO()
    # the sides import the context shim from the directory they run in
    sys.path.insert(0, str(driver_file.parent))
    try:
        with contextlib.redirect_stderr(buf):
            run_pair(str(driver_file), entry=None, calls=None)
    finally:
        sys.path.remove(str(driver_file.parent))
    return _verdict_of(buf.getvalue())


def _scenario_dir(root: Path, name: str, files: dict) -> Path:
    d = root / name
    shutil.copytree(EX_DIR, d, ignore=shutil.ignore_patterns(
        "__pycache__", "review.json", "meta.json"))
    for key, text in files.items():
        (d / TTLS[key]).write_text(text)
    return d


verdicts = {"shipped": _run(EX_DIR / "driver.py")}
with tempfile.TemporaryDirectory() as tmp:
    for name, files in SCENARIOS.items():
        d = _scenario_dir(Path(tmp), name, files)
        verdicts[name] = _run(d / "driver.py")
first = verdicts["shipped"]
VERDICT = {
    "example": EX_DIR.name,
    "equivalent": all(v["equivalent"] for v in verdicts.values()),
    "method": f"module-state x {len(verdicts)} inputs",
    "diffs": [f"[{n}] {d}" for n, v in verdicts.items() for d in v["diffs"]],
    "error": "; ".join(f"[{n}] {v['error']}" for n, v in verdicts.items() if v["error"]) or None,
    "sides": first["sides"],
    "scenarios": sorted(verdicts),
}
_emit(VERDICT)
