"""Validation driver for fair-workflows__fairworkflows__fairworkflows_rdf_wrapper.py__RdfWrapper__uri_is_subject_in_rdf.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). `fixture.ttl` is parsed fresh for each side.

The entry point takes three arguments (uri, rdf, force), not just a graph,
so `calls` supplies (uri, fixture graph, force) explicitly rather than
relying on run_pair's default single-argument call.

Every call is compared by its outcome: the harness compares a raise on
both sides as a value (exception type and message), so the branch that
RAISES ValueError (uri not a subject, force=False) is exercised directly.
The force=True branch's only effect is `warnings.warn(message,
UserWarning)`; the driver turns UserWarning into an error for the whole run
so that this warning, too, becomes a compared outcome (type and message)
instead of an unobserved side effect. Nothing follows the warning in the
region, so this changes no other behaviour.

The repository's two callers (fairworkflows/fairworkflow.py:68,
fairworkflows/fairstep.py:157) pass the user's `uri` through, a `str` in
its tests; a `URIRef` is also accepted, and one call passes one.

  * uri present as a subject (several solutions: it also carries a second
    triple), force=False -> no warning, no exception, returns None.
  * uri present in the graph only as an OBJECT, force=True -> warns.
  * uri absent from the graph altogether, force=True -> the zero-solution
    case; warns.
  * the same three situations with force=False -> the absent and
    object-only URIs raise ValueError. These kill the subject widened to
    `?s` (no raise) and the subject moved to the object position.
  * a uri used only as a PREDICATE, force=False -> raises: kills the
    subject moved to the predicate position.
  * uri present, given as a `URIRef` rather than a `str`, force=False ->
    returns None on both sides.
  * two more subjects, force=False -> None: ex:other (one triple, IRI
    object) and ex:onlyQ (its only predicate is ex:q). With ex:present
    they kill the `?p` or `?o` wildcard narrowed to a constant.
"""
import warnings
from pathlib import Path

import rdflib

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"

# the force=True branch's warning becomes a compared outcome
warnings.simplefilter("error", UserWarning)


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
        _case("http://example.org/absent", False),
        _case("http://example.org/onlyAnObject", False),
        _case("http://example.org/p", False),
        _case(rdflib.URIRef("http://example.org/present"), False),
        _case("http://example.org/other", False),
        _case("http://example.org/onlyQ", False),
    ],
)
