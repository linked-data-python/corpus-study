"""Validation driver for aigora-de__rdf-construct__src_rdf_construct_shacl_converters.py__DomainRangeConverter_convert_for_class.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The region is extracted as a plain function of ``(self, cls, source_graph,
config)`` rather than a bound method, so the fixture supplies all four
arguments explicitly instead of relying on the harness's single-graph
default.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair
from shacl_context import ConverterSelf, ShaclConfig

EX = Namespace("http://example.org/")
_FIXTURE = Path(__file__).parent / "fixture.ttl"


def _case():
    return (
        (ConverterSelf(), EX.Person, fixture_graph(_FIXTURE), ShaclConfig()),
        {},
    )


VERDICT = run_pair(
    __file__,
    entry='convert_for_class',
    fixture="fixture.ttl",
    calls=[_case],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
