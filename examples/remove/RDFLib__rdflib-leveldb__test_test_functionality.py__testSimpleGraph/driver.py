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

Neighbours of the removed triple.  The region fixes its own data and asserts
exact counts on it (`len(g) == 3`, "tarek doesn't like cheese" is 0 matches),
so the fixture cannot seed a neighbour of `(tarek, likes, pizza)` in
<urn:graph> without breaking the region's own asserts.  What the driver can do
is add them at the one moment the asserts are over and the removal is about to
happen: the `Dataset` handed over returns, for <urn:graph>, a `Graph` whose
`remove()` first adds, once, `tarek likes cheese` (same subject and predicate,
other object) and `tarek eats pizza` (same subject and object, other
predicate); `bob likes pizza`, which the region itself adds, is the third
neighbour (same predicate and object, other subject).  All three must survive
the removal of the one fully bound triple, and the final-state comparison
(exact quad sets) sees any that does not.  The hook is the same on both sides
(original: `g.remove(...)`; translation: `-{ }` ends in `graph.remove(...)`),
and it adds the same two triples whatever pattern the removal receives, so a
`-{ }` widened to a variable in any one position removes a neighbour and
makes the two final states differ.

What this does NOT cover: the region's last line, a query after the removal
whose result is dropped.  The original executes it and throws the answer
away; `s{ }` only builds a lazy query that nothing runs.  No change to that
query can show in the graph, the return value or the output: the mutant that
changes its `<urn:pizza>` into `<urn:cheese>` survives (it was run), and it is
an equivalent mutant, not a weakness a driver can mend.
"""
from pathlib import Path
from rdflib import Graph, URIRef
from rdfeval.harness import run_pair

_FIXTURE = Path(__file__).parent / "fixture.ttl"


_TAREK = URIRef("urn:tarek")
_LIKES = URIRef("urn:likes")
_NEIGHBOURS = (
    (_TAREK, _LIKES, URIRef("urn:cheese")),   # same subject and predicate
    (_TAREK, URIRef("urn:eats"), URIRef("urn:pizza")),  # same subject, object
)


class _Context(Graph):
    """A named graph that, before its first removal, gains two neighbours."""

    _seeded = False

    def remove(self, triple):
        if not self._seeded:
            self._seeded = True
            for t in _NEIGHBOURS:
                self.add(t)
        return super().remove(triple)


class _DatasetProxy:
    """Forwards to an `rdflib.Dataset` without being a `Graph` instance."""

    def get_context(self, identifier, quoted=False, base=None):
        if identifier != URIRef("urn:graph"):
            return self._ds.get_context(identifier, quoted, base)
        return _Context(store=self._ds.store, identifier=identifier,
                        namespace_manager=self._ds.namespace_manager,
                        base=base)

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
