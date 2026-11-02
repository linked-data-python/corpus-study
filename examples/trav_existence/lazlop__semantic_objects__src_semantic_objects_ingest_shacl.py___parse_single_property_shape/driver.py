"""Validation driver for lazlop__semantic_objects__src_semantic_objects_ingest_shacl.py___parse_single_property_shape.

The region reads one SHACL property shape (a blank node, `bn`) and returns a
PropertyShapeIR (a field) or a ComplexConstraintIR (not reducible).  Its
existence reads are `(bn, sh:sparql, None) in g` and
`any((bn, pred, None) in g for pred in sh:or / sh:xone)`; the value reads
(`g.value(...)`) decide the rest.  The IR classes are dataclasses, compared
field by field (including `raw_turtle`, the serialised sub-graph).

Calls: one per property shape of fixture.ttl (K01..K25, see the comments
there for the branch each reaches).  `bn` is the single sh:property blank node
of ex:Kxx, found with g.value.  Neighbours that must not match: K20 (look-alike
predicates in another namespace), K21 (a sibling property shape carries
sh:sparql / sh:or, the one asked about does not), ex:Elsewhere (same
predicates on another node).
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")
SH = Namespace("http://www.w3.org/ns/shacl#")


def _case(name, nth=0):
    def make():
        g = fixture_graph(FIXTURE)
        shapes = sorted(g.objects(EX[name], SH.property),
                        key=lambda b: str(sorted(map(str, g.objects(b, SH.path)))))
        return (g, shapes[nth]), {}
    return make


def _sibling(name, path):
    """The property shape of ex:Kxx whose sh:path is ex:<path>."""
    def make():
        g = fixture_graph(FIXTURE)
        (bn,) = [b for b in g.objects(EX[name], SH.property)
                 if (b, SH.path, EX[path]) in g]
        return (g, bn), {}
    return make


NAMES = ["K%02d" % i for i in range(1, 26) if i != 21]

VERDICT = run_pair(
    __file__,
    entry='_parse_single_property_shape',
    calls=[_case(n) for n in NAMES] + [
        _sibling("K21", "hasMode"),    # direct class; the sibling's sparql / or must not leak
        _sibling("K21", "hasOther"),   # sparql wins over or
    ],
)
