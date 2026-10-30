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

Calls (the last four added by the 2026-10-30 repair):

- ``ex:Person`` with ``ShaclConfig()`` (both flags True): every read runs;
- ``ex:Person`` with both flags False: neither the label nor the comment
  read may run -- kills ``if config.include_*:`` -> ``if True:``;
- ``ex:Person`` with only one flag True, each way: the two guards are
  independent, so swapping them or reading one under the other's flag fails;
- ``ex:Place``, which no property has as domain: zero solutions, ``[]``.

The fixture adds an empty label and comment (``if label:`` is false on
``""``), a range declared ``rdfs:Datatype`` outside XSD, several labels on one
property (``.first()`` must take what ``value()`` takes), and neighbours that
share two terms of a motif under another predicate (``ex:related rdfs:seeAlso
ex:Person``; ``ex:knows rdfs:seeAlso ...``), which kill the mutants that widen
a bound predicate to a variable.
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


def _case_with(cls_local, labels, descriptions):
    def make():
        config = ShaclConfig(include_labels=labels,
                             include_descriptions=descriptions)
        return (ConverterSelf(), EX[cls_local], fixture_graph(_FIXTURE),
                config), {}
    return make


VERDICT = run_pair(
    __file__,
    entry='convert_for_class',
    fixture="fixture.ttl",
    calls=[_case,
           _case_with("Person", False, False),
           _case_with("Person", True, False),
           _case_with("Person", False, True),
           _case_with("Place", True, True)],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
