"""Validation driver for d3fend__d3fend-ontology__src_util_update_atlas.py__add_revoked.

`add_revoked(graph, tech)` looks for the technique's ATLAS id as the object of
ANY triple (`(None, None, Literal(atlas_id)) in graph`), then reads
`owl:deprecated` of the technique's IRI (`graph.value(atlas_uri, owl.deprecated)`)
and, if it is None, adds three triples and returns 1; otherwise it returns 0.
The graph is the argument that gets mutated, and the return value is 0/1:
both are compared, plus any exception (a raise is compared like a value).

`fixture.ttl` is parsed afresh for each side (see its header for the cases).
The calls are indexed by technique, and cover: not deprecated (annotations
added), deprecated true (untouched), deprecated false (a falsy value that is
not None: untouched), id missing, id only language-tagged/typed (a plain
`Literal(atlas_id)` does not match those), deprecation on another subject
only, an id shared by two subjects, a near-miss deprecation property, an
unknown technique, a mitre-atlas reference preceded by another source, a
`revoked_by` that is not a string, and the techniques with no mitre-atlas
reference (atlas_id None: `_XMLNS + None` raises TypeError).
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"


def tech(atlas_id, revoked_by="AML.T0099", refs=None):
    if refs is None:
        refs = [{"source_name": "mitre-atlas", "external_id": atlas_id}]
    return {"revoked_by": revoked_by, "data": {"external_references": refs}}


def call(t):
    def c():
        return ((fixture_graph(FIXTURE), t), {})
    return c


CALLS = [
    call(tech("AML.T0001")),                                  # added, returns 1
    call(tech("AML.T0002")),                                  # deprecated true: 0
    call(tech("AML.T0003")),                                  # deprecated false: 0
    call(tech("AML.T0004")),                                  # no literal for the id: 0
    call(tech("AML.T0005")),                                  # id only as @en / ^^xsd:token: 0
    call(tech("AML.T0006")),                                  # shared id, own IRI not deprecated: 1
    call(tech("AML.T0007")),                                  # shared id, own IRI not deprecated: 1
    call(tech("AML.T0008")),                                  # id of a deprecated one: 0
    call(tech("AML.T0010")),                                  # near-miss property: 1
    call(tech("AML.T0099")),                                  # unknown technique: 0
    call(tech("AML.T0001", revoked_by=42)),                   # non-string revoked_by
    call(tech("AML.T0001", revoked_by="AML.T0002 — é")),
    call(tech(None, refs=[{"source_name": "other", "external_id": "AML.T0001"},
                          {"source_name": "mitre-atlas", "external_id": "AML.T0001"}])),  # 1: first mitre-atlas ref
    call(tech(None, refs=[{"source_name": "mitre-atlas", "external_id": "AML.T0001"},
                          {"source_name": "mitre-atlas", "external_id": "AML.T0002"}])),  # the first one wins: 1
    call(tech(None, refs=[{"source_name": "other", "external_id": "AML.T0001"}])),    # none: TypeError
    call(tech(None, refs=[])),                                # no references: TypeError
    call(tech(None, refs=[{"source_name": "mitre-atlas"}])),  # mitre-atlas without id: TypeError
]

VERDICT = run_pair(
    __file__,
    entry="add_revoked",
    calls=CALLS,
    fixture=None,
)
