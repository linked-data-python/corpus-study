"""Validation driver for deepin-community__lv2__scripts_lv2_check_specification.py___has_property.

This region READS a graph, so the oracle is not isomorphism (meta.json's
`oracle` field is a pipeline default computed from `rdf_ops`, which is 0
here because `model` carries no annotation -- see original.py/translated.ldpy
for the restored binding) but the equality of the values both versions
produce from the same input graph (design record corpus/405).

`_has_property(model, subject, predicate)` takes THREE arguments, so the
default `fixture=` calling convention (entry called with just the parsed
graph) does not fit: `calls` is given explicitly, one call per
(subject, predicate) pair in fixture.ttl, each re-parsing the fixture fresh.
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"


def _case(subject, predicate):
    s, p = URIRef(EX + subject), URIRef(EX + predicate)
    return lambda: ((fixture_graph(FIXTURE), s, p), {})


VERDICT = run_pair(
    __file__,
    entry='_has_property',
    fixture="fixture.ttl",
    calls=[
        _case("s1", "p1"),  # two solutions -> True
        _case("s1", "p2"),  # one solution -> True
        _case("s1", "p3"),  # predicate never on this subject -> False
        _case("s2", "p2"),  # predicate exists, but not on this subject -> False
        _case("s3", "p1"),  # subject absent from the graph entirely -> False
    ],
)
