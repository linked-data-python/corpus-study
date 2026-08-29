"""Validation driver for aigora-de__rdf-construct__src_rdf_construct_describe_documentation.py___has_label.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_has_label(graph, subject)` takes TWO arguments, not one, so the default
`fixture=` calling convention (entry called with the parsed graph as its
sole argument) does not fit here: `calls` is given explicitly, one call per
test subject in fixture.ttl, each re-parsing the fixture fresh (so a call
cannot leak state into the next, or into the other side).
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"

# One call per subject in fixture.ttl: three that resolve through a
# different LABEL_PREDICATES member each, one with only non-label
# predicates, one absent from the graph entirely (both False cases).
_SUBJECTS = [
    URIRef(EX + "hasLabel"),
    URIRef(EX + "hasAltLabel"),
    URIRef(EX + "hasTitle"),
    URIRef(EX + "noLabel"),
    URIRef(EX + "isolated"),
]

VERDICT = run_pair(
    __file__,
    entry='_has_label',
    fixture="fixture.ttl",
    calls=[(lambda s=s: ((fixture_graph(FIXTURE), s), {})) for s in _SUBJECTS],
)
