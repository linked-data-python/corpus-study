"""Validation driver for csvwlib's TestToRDFConverter.change_urls_in_result.

The region walks a graph and rewrites, in place, every triple whose subject,
predicate or object contains the remote test location (a substring test, so a
literal containing it is concerned too, and comes out as an IRI).  It
returns nothing: the oracle is the mutation of the graph argument, which the
harness compares between the sides.

`fixture.ttl` holds the cases: the location in the subject only, the
predicate only, the object only, all three of one triple, a literal that
contains it (plain and language-tagged), a blank node subject, and
neighbours that must stay put (other locations, an already local IRI, a
number).  Four calls vary the pair of locations; the last one has a remote
location that matches nothing.
"""
from pathlib import Path
from types import SimpleNamespace

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


def _call(remote, local):
    def make():
        me = SimpleNamespace(_remote_tests_location=remote, _tests_location=local)
        return (me, fixture_graph(FIXTURE)), {}
    return make


CALLS = [
    _call("http://remote.example/tests/", "http://local.example/tests/"),
    _call("http://remote.example/", "file:///data/"),
    _call("http://remote.example/other/", "http://local.example/other/"),
    _call("http://nowhere.example/", "http://local.example/"),
]

VERDICT = run_pair(
    __file__,
    entry='change_urls_in_result',
    fixture="fixture.ttl",
    calls=CALLS,
)
