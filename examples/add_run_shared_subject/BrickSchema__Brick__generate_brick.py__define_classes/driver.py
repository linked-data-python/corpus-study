"""Validation driver for BrickSchema__Brick__generate_brick.py__define_classes.

Establishes semantic equivalence of original.py and translated.ldpy by
calling `define_classes` on a small definitions tree that exercises every
branch touched by the region's `add_run_shared_subject` triples: a plain
subclass, a punned class, a nested subclass, an extra `parents` entry, an
alias (which itself walks `graph.objects(...)` to copy `subClassOf`
parents), and a non-list extra property. Each call gets a fresh graph so
mutations on one side cannot leak into the other's.

On top of run_pair (kept as it was), two things the repository observes and
run_pair does not compare:

  * prefix bindings. generate_brick.py:73-74 builds `G` and binds it with
    bricksrc.namespaces.bind_prefixes (namespaces.py:35-56) before any
    define_classes call, then serialises it to Brick.ttl
    (generate_brick.py:1123, 1146, 1176). `@graph graph` binds the block's
    13 prefixes into that graph (record ldpy/027): under another name, one
    of them would REPLACE the repository's binding for the same namespace
    (rdflib's bind overrides) and change Brick.ttl. Case "G" passes a graph
    bound exactly as bind_prefixes binds it; case "extension_graph" passes
    the plain Graph() of generate_brick.py:1088-1096. For each, every
    binding of the original's graph must be in the translation's (extras
    tolerated), and the triples must be isomorphic.
  * the `logging` journal: the region warns once per class without tags
    (HVAC's empty list, AHU's missing key) -- both sides must log the same
    records, in the same order.
"""
import contextlib
import io
import logging
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair
from rdflib import Graph, Namespace, URIRef

PARENT = URIRef("https://brickschema.org/schema/Brick#Equipment")

DEFINITIONS = {
    "HVAC": {
        "tags": [],
        "parents": [URIRef("https://brickschema.org/schema/Brick#Asset")],
        "subclasses": {
            "AHU": {},
        },
        "aliases": [URIRef("https://brickschema.org/schema/Brick#AirHandler")],
        URIRef("https://brickschema.org/schema/Brick#hasFlag"):
            URIRef("https://brickschema.org/schema/Brick#Equipment"),
    },
}


def _case():
    g = Graph()
    return ((dict(DEFINITIONS), PARENT), {"pun_classes": True, "graph": g})


# bricksrc/namespaces.py:35-56, verbatim prefixes and IRIs
REPO_BINDINGS = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "dcterms": "http://purl.org/dc/terms/",
    "sdo": "http://schema.org/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "sosa": "http://www.w3.org/ns/sosa/",
    "sh": "http://www.w3.org/ns/shacl#",
    "brick": "https://brickschema.org/schema/Brick#",
    "ref": "https://brickschema.org/schema/Brick/ref#",
    "tag": "https://brickschema.org/schema/BrickTag#",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "bsh": "https://brickschema.org/schema/BrickShape#",
    "qudtqk": "http://qudt.org/vocab/quantitykind/",
    "qudt": "http://qudt.org/schema/qudt/",
    "unit": "http://qudt.org/vocab/unit/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "bacnet": "http://data.ashrae.org/bacnet/",
    "ifc": "https://brickschema.org/extension/ifc#",
    "s223": "http://data.ashrae.org/standard223#",
    "rec": "https://w3id.org/rec#",
}


def _repo_G():
    g = Graph()
    for prefix, iri in REPO_BINDINGS.items():
        g.bind(prefix, Namespace(iri))
    return g


EXTRA_CASES = [("G", _repo_G), ("extension_graph", Graph)]


class _Journal(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append((record.name, record.levelname,
                             record.getMessage()))


def _run(fn, graph):
    journal = _Journal()
    root = logging.getLogger()
    root.addHandler(journal)
    try:
        fn(dict(DEFINITIONS), PARENT, pun_classes=True, graph=graph)
    finally:
        root.removeHandler(journal)
    return journal.records


with contextlib.redirect_stderr(io.StringIO()):       # this driver emits
    VERDICT = run_pair(
        __file__,
        entry='define_classes',
        calls=[_case, _case],
    )

ex_dir = Path(__file__).resolve().parent
try:
    ns_o, _ = harness._exec_python(ex_dir / "original.py")
    ns_t, _ = harness._exec_ldpy(ex_dir / "translated.ldpy")
    for label, make in EXTRA_CASES:
        go, gt = make(), make()
        with contextlib.redirect_stderr(io.StringIO()):  # lastResort handler
            lo = _run(ns_o["define_classes"], go)
            lt = _run(ns_t["define_classes"], gt)
        if lo != lt:
            VERDICT["diffs"].append(f"{label}: logging differs ({lo} vs {lt})")
        if not lo:
            VERDICT["diffs"].append(f"{label}: no warning logged, "
                                    "the journal compares nothing")
        if not harness.graphs_isomorphic(go, gt):
            VERDICT["diffs"].append(f"{label}: graphs not isomorphic "
                                    f"({len(go)} vs {len(gt)} triples)")
        lost = set(go.namespaces()) - set(gt.namespaces())
        if lost:
            VERDICT["diffs"].append(
                f"{label}: prefix bindings lost {sorted(lost)}")
except Exception:
    import traceback
    VERDICT["error"] = traceback.format_exc(limit=8)
VERDICT["method"] = (f"{VERDICT.get('method')} + repo-bound graph "
                     "(bindings, logging)")
VERDICT["equivalent"] = not VERDICT["diffs"] and not VERDICT.get("error")
harness._emit(VERDICT)
