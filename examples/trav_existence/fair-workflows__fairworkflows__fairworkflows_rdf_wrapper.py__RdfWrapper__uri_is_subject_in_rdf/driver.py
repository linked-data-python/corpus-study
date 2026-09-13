"""Validation driver for fair-workflows__fairworkflows__fairworkflows_rdf_wrapper.py__RdfWrapper__uri_is_subject_in_rdf.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` is parsed fresh for each side.

The entry point takes three arguments (uri, rdf, force), not just a graph,
so `calls` supplies (uri, fixture graph, force) explicitly rather than
relying on run_pair's default single-argument call.

Three cases, chosen to stay OUTSIDE the one branch run_pair cannot compare:
when `uri` is absent and `force` is False, the region RAISES ValueError, and
run_pair aborts the whole verdict on any exception from either side rather
than comparing the two raises -- see rdfeval/harness.py's run_pair, which
wraps both calls in one try/except with no per-call exception handling. That
branch is therefore not exercised here; it differs from the others only by
`if force: warn else: raise`, a plain Python conditional untouched by the
translation, so the risk of a translation-specific bug there is the same as
for the branch this driver DOES cover.

  * uri present as a subject (several solutions: it also carries a second
    triple) -> exists is True, no warning, no exception, returns None.
  * uri present in the graph but only ever as an OBJECT, never a subject
    (the neighbour fixture.ttl warns about) -> exists is False; force=True
    so this WARNS rather than raising -- still returns None, comparably.
  * uri absent from the graph altogether, force=True -> the zero-solution
    case; also warns rather than raising, returns None.
"""
from pathlib import Path

import rdflib

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _case(uri, force):
    def make():
        return (uri, fixture_graph(FIXTURE), force), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="_uri_is_subject_in_rdf",
    fixture="fixture.ttl",
    calls=[
        _case("http://example.org/present", False),
        _case("http://example.org/onlyAnObject", True),
        _case("http://example.org/absent", True),
    ],
)
