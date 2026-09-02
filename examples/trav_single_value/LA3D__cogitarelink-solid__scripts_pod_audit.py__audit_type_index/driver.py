"""Validation driver for LA3D__cogitarelink-solid__scripts_pod_audit.py__audit_type_index.

Establishes semantic equivalence of original.py and translated.ldpy.

`audit_type_index_body` is the wrapped statement region (see original.py's
docstring): it takes `ti_g`, `findings`, `canon_base`, `pod_base`,
`container_classes`, `heads` as parameters instead of the bindings the
enclosing `async def audit_type_index` supplies in the source file. It
returns nothing -- everything it does is visible through the mutated
`findings` / `container_classes` / `heads` arguments, which `run_pair`
compares alongside the (here, isomorphic-by-construction) `ti_g` graph.

`ordered=False`: the loop iterates `ti_g.subjects(RDF.type, ...)` /
`m{ ?reg rdf:type solid:TypeRegistration }` and never sorts, so `findings`
and `heads` are compared as multisets; the lists nested inside
`container_classes` (per-container accumulated classes) get the same
treatment since `ordered=False` normalises recursively.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair

FIXTURE = Path(__file__).parent / "fixture.ttl"
CANON_BASE = "https://canon.example/vault/"
POD_BASE = "https://reachable.example/vault/"


def _call():
    # Parsed fresh per side (run_pair invokes this callable once for
    # original.py, once for translated.ldpy) so a graph mutation on one
    # side -- there is none here, the region only reads ti_g -- could never
    # leak into the other.
    ti_g = Graph().parse(str(FIXTURE), format="turtle")
    findings = []
    container_classes = {}
    heads = []
    return (ti_g, findings, CANON_BASE, POD_BASE, container_classes, heads), {}


VERDICT = run_pair(
    __file__,
    entry='audit_type_index_body',
    calls=[_call],
    ordered=False,
)
