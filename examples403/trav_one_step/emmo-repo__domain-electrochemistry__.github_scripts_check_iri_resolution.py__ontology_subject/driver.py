"""Validation driver for emmo-repo__domain-electrochemistry__.github_scripts_check_iri_resolution.py__ontology_subject.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`ontology_subject` takes a second argument (`source`, used only in the
raised message on the empty-graph path) beyond the graph, so the single
positional argument `fixture=` alone would build does not fit -- `calls=`
supplies both.

The fixture is part of the translation: it holds several solutions of the
pattern the region reads and neighbouring triples that must NOT match. It
does NOT encode the zero-solution case as a call here -- see fixture.ttl for
why (the region raises rather than returning None there, and the harness
cannot compare a raised exception).
"""
from rdfeval.harness import fixture_graph, run_pair


def _call():
    return (fixture_graph("fixture.ttl"), "test-source"), {}


VERDICT = run_pair(
    __file__,
    entry='ontology_subject',
    fixture="fixture.ttl",
    calls=[_call],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets. Not that
    # it matters here: the entry point returns a single term, not a sequence.
)
