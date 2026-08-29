"""Validation driver for BD2KOnFHIR__fhirtordf__fhirtordf_rdfsupport_rdfcompare.py__rdf_compare_split_primary_subjects.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`run_primary_subjects` is the context-restoration wrapper (see meta.json,
original.py): the region's own `primary_subjects` reads a free variable `g1`
inherited from its home closure `rdf_compare_split(g1, g2, ...)`, which
extraction severs. The wrapper rebinds the module global to this call's own
argument right before calling the untouched region.

Two calls: the fixture graph (three URIRef subjects, a neighbouring
object-only URIRef, and two BNode subjects, one with an incoming edge and one
without -- neither ever reaches the output, since the region's own "orphan"
check is dead code, see meta.json), and an empty graph for the zero-solution
case.
"""
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

VERDICT = run_pair(
    __file__,
    entry="run_primary_subjects",
    fixture="fixture.ttl",
    calls=[
        lambda: ((fixture_graph(FIXTURE),), {}),
        lambda: ((Graph(),), {}),
    ],
)
