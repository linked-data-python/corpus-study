"""Validation driver for RDFLib__rdflib-leveldb__test_test_functionality.py__testSimpleGraph.

The real `getgraph` pytest fixture (see the upstream repository's own
conftest-style fixture in test/test_functionality.py) is a
`ConjunctiveGraph(store="LevelDB")` backed by an on-disk LevelDB store: an
external C-extension dependency out of reach here, and one the region's own
body never actually needs -- it only calls `graph.get_context(...)`, `.add`/
`.remove`/`.query`/`.triples` on the graph it gets, all of which an in-memory
`rdflib.Dataset` supports identically. This driver substitutes a fresh
`Dataset()` per call, matching the fixture's *interface* (named-graph
contexts) rather than its storage backend.

The region reads AND writes: it builds its own data inside two named graphs,
then reads it back through both a literal SPARQL query, initBindings, and
`.triples()` patterns (all guarded by `assert`, so a wrong read raises and
the pilot catches it as an error, not a silent pass), then removes one triple
and re-queries. Its own return value is always `None` -- what needs to be
compared is the resulting graph, so `fixture.ttl` is loaded into a `Dataset`
and passed as `getgraph`; run_pair's built-in argument comparison then
isomorphism-compares the two Datasets *after* the call (see meta.json for
why a `Dataset` cannot go through the default `fixture=` wiring: `Dataset`
iterates as quads, and `rdflib.compare.to_isomorphic` -- what run_pair uses
for a bare `Graph` argument -- raises on that. `_DatasetProxy` below is the
same sidestep the sibling region testUpdateWithInitNs/driver.py uses: it is
not an `isinstance(..., Graph)`, so run_pair's generic Graph branch is
skipped, and it supplies its own `__eq__` by exact quad-set equality (sound
here since neither side nor the fixture ever mints a blank node).

`fixture.ttl` seeds unrelated data in the DEFAULT graph only (see its own
header): the region's own asserted counts already exercise the
several-solutions / zero-solution / non-matching-neighbour cases the reading
oracle asks for, against the two named graphs the region itself populates;
the fixture's job is only to prove that reading is scoped to the right named
graph and does not pick up the unrelated data.
"""
from pathlib import Path
from rdfeval.harness import run_pair

_FIXTURE = Path(__file__).parent / "fixture.ttl"


class _DatasetProxy:
    """Forwards to an `rdflib.Dataset` without being a `Graph` instance."""

    def __init__(self, ds):
        self._ds = ds

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        return getattr(self._ds, name)

    def _quads(self):
        return {(s, p, o, c) for s, p, o, c in self._ds.quads((None, None, None, None))}

    def __eq__(self, other):
        if not isinstance(other, _DatasetProxy):
            return NotImplemented
        return self._quads() == other._quads()

    def __hash__(self):
        return id(self)


def _fresh_dataset():
    from rdflib import Dataset
    ds = Dataset()
    ds.parse(source=str(_FIXTURE), format="turtle")
    return (_DatasetProxy(ds),), {}


VERDICT = run_pair(
    __file__,
    entry='testSimpleGraph',
    calls=[_fresh_dataset],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
