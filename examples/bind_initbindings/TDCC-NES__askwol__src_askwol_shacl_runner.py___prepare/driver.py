"""Validation driver for TDCC-NES__askwol__src_askwol_shacl_runner.py___prepare.

This region is NOT-EXPRESSIBLE in ldpy (see meta.json): `_prepare` is a
generic `functools.lru_cache`d factory -- `query_text`, `init_ns_items` and
`base` all arrive as runtime parameters, from many call sites across the
askwol codebase (see `_cached_query`, the monkey-patch of `Graph.query` this
helper backs). `s{ }` requires its query text to be written literally at the
island site so it can be validated at transpile time (querying.md); there is
no island for "compile this string, handed to me at runtime, into a prepared
query". `translated.ldpy` is therefore byte-identical to `original.py` (down
to the demo harness) -- the transparent case recorded in DESIGN_CHOICES
ldpy/012 ("no RDF structure reachable by the notation" -> no island used).

`_prepare` returns a prepared-query object with no useful `__eq__` (two
independently built instances of the same query are never `==`), so
comparing it directly -- what run_pair's entry/calls path does by default --
would report a spurious diff regardless of translation correctness. The
`demo` harness both files carry identically makes the region's true,
observable behaviour comparable instead: `cached` (a second call with the
same arguments is served from the lru_cache, proving `_prepare` itself
still behaves as a cache) and `rows` (the prepared query, run against
`fixture.ttl`, produces the expected solutions).

Two calls: a query that matches two of the fixture's three subjects (the
third has the wrong rdf:type -- the neighbourhood that must not match), and
a query for a type with no member at all (the zero-solution case).
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")


def call(query_text):
    def _make():
        graph = fixture_graph(FIXTURE)
        init_ns_items = (("ex", EX),)
        return (query_text, init_ns_items, None, graph), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry="demo",
    fixture="fixture.ttl",
    ordered=True,
    calls=[
        call("SELECT ?s WHERE { ?s a ex:Thing }"),        # two solutions
        call("SELECT ?s WHERE { ?s a ex:Nonexistent }"),  # zero solutions
    ],
)
