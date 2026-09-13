"""Validation driver for RDFLib__VocPrez__vocprez_model_concept.py__ConceptRenderer__render_skos_rdf.

The region returns a Flask ``Response`` wrapping a serialised graph: raw
serialisation is never a safe comparison (bnode ids, triple order), so this
driver calls the entry point on both sides, re-parses each Turtle body into
a fresh graph, and lets the harness compare THOSE by isomorphism instead of
comparing the ``Response`` objects (or their bytes) directly.
"""
import traceback
from pathlib import Path
from rdflib import Graph
from rdfeval.harness import _exec_python, _exec_ldpy, _compare_value, _emit


class _Prop:
    def __init__(self, uri, value):
        self.uri = uri
        self.value = value


def _make_self():
    class _Self:
        pass

    self = _Self()

    class _Concept:
        pass

    concept = _Concept()
    concept.vocab_uri = "http://example.org/scheme/1"
    concept.uri = "http://example.org/concept/1"
    concept.prefLabel = "Example Concept"
    concept.definition = "An example concept for testing."
    concept.related_instances = {
        "broader": [
            _Prop("http://www.w3.org/2004/02/skos/core#broader",
                  "http://example.org/concept/0"),
            _Prop("http://www.w3.org/2004/02/skos/core#note", "a plain note"),
        ],
    }
    concept.other_properties = [
        [_Prop("http://purl.org/dc/terms/source",
               "http://example.org/source/1")],
        [_Prop("http://purl.org/dc/terms/created", "2020-01-01")],
    ]

    self.concept = concept
    self.mediatype = "text/turtle"
    self.headers = {}
    return self


ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:_render_skos_rdf (re-parsed graphs)",
                 "diffs": [], "error": None}

try:
    ns_o, _ = _exec_python(ex_dir / "original.py")
    ns_t, _ = _exec_ldpy(ex_dir / "translated.ldpy")
    fo, ft = ns_o["_render_skos_rdf"], ns_t["_render_skos_rdf"]
    ro = fo(_make_self())
    rt = ft(_make_self())
    go = Graph().parse(data=ro.get_data(as_text=True), format="turtle")
    gt = Graph().parse(data=rt.get_data(as_text=True), format="turtle")
    diffs: list[str] = []
    _compare_value(go, gt, "graph", diffs)
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
VERDICT = verdict
