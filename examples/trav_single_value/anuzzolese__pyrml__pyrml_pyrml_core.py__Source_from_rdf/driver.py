"""Validation driver for anuzzolese__pyrml__pyrml_pyrml_core.py__Source_from_rdf.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`from_rdf(g, parent)` takes two arguments, not the single graph the
`fixture=` shortcut would pass alone, so `calls=` is built explicitly here,
reading the fixture and calling the entry point on `ex:parent1`.
"""
from pathlib import Path
from rdflib import URIRef

from rdfeval.harness import run_pair, fixture_graph

EX = "http://example.org/"
FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _case(parent_local):
    def make():
        g = fixture_graph(FIXTURE)
        return ((g, URIRef(EX + parent_local)), {})
    return make


VERDICT = run_pair(
    __file__,
    entry='from_rdf',
    calls=[_case("parent1"), _case("parent3")],
    # no store promises the order g.objects() yields rml:source in:
    ordered=False,
)
