"""Validation driver for BD2KOnFHIR__fhirtordf__fhirtordf_rdfsupport_fhirgraphutils.py__extension.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

Three calls: the target node whose matching extension carries an
Extension.value* predicate (the single expected solution of the fused join),
the second patient whose only extension never carries Extension.value*
(zero-solution case), and a node with no fhir:Element.extension triples at
all (also zero-solution, from a different angle: no ext candidate exists).
"""
from pathlib import Path

from rdflib import URIRef

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = "http://example.org/"


def _case(node, pred):
    return lambda: ((fixture_graph(FIXTURE), URIRef(node), pred), {})


VERDICT = run_pair(
    __file__,
    entry="extension",
    fixture="fixture.ttl",
    calls=[
        _case(EX + "patient1", EX + "ext/target"),
        _case(EX + "patient2", EX + "ext/target"),
        _case(EX + "no-such-node", EX + "ext/target"),
    ],
)
