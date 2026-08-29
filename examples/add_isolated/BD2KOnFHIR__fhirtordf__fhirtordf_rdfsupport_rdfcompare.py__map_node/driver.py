"""Validation driver for BD2KOnFHIR__fhirtordf__fhirtordf_rdfsupport_rdfcompare.py__map_node.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

map_node(s, sk_s, gin, gout) takes four positional arguments, not just the
fixture graph, so `calls` supplies (s, sk_s, gin, gout) explicitly; gin comes
from fixture.ttl and gout is a fresh Graph, both rebuilt on every `_make_call`
invocation (run_pair calls it once per side, so neither side's writes can
leak into the other's). run_pair compares every positional argument after the
call, so the mutated `gout` -- by isomorphism, since it is a plain rdflib
Graph -- is what actually proves the +{ } rewrite equivalent to the two
gout.add(...) calls it replaces; map_node itself returns None.
"""
from pathlib import Path

from rdflib import Graph, URIRef

from rdfeval.harness import fixture_graph, run_pair

_HERE = Path(__file__).resolve().parent
_S0 = URIRef("http://example.org/s0")
_SK_S0 = URIRef("http://example.org/sk-s0")


def _make_call():
    gin = fixture_graph(_HERE / "fixture.ttl")
    gout = Graph()
    return (_S0, _SK_S0, gin, gout), {}


VERDICT = run_pair(
    __file__,
    entry="map_node",
    fixture="fixture.ttl",
    calls=[_make_call],
)
