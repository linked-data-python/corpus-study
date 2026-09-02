"""Validation driver for RDFLib__rdflib-leveldb__test_test_functionality.py__testUpdateWithInitNs.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The region needs `graph.get_context(...)` and `GRAPH ns:graph { ... }` in an
update — named-graph operations that a plain `rdflib.Graph` does not
support, so the fixture is loaded into an `rdflib.Dataset` instead. Two
consequences follow:

- The default `fixture=` wiring in `rdfeval.harness.run_pair` always parses
  into a plain `Graph`, so this driver builds its own loader and passes it
  via `calls=` (one fresh `Dataset` per side, matching what `fixture=` does
  internally).
- `run_pair` auto-compares every call argument, and for a `Graph` it does so
  via `rdflib.compare.to_isomorphic` — which assumes triples. A `Dataset`
  iterates as quads, and `to_isomorphic` crashes on it
  (`ValueError: too many values to unpack`, inside `Graph.__iadd__`). That is
  an rdflib/rdfeval interaction bug, not a property of the translation, and
  fixing it would mean editing `rdfeval/harness.py`, which is out of scope
  for a translation lot. `_DatasetProxy` below sidesteps it: it is not an
  `instanceof Graph`, so the harness's generic branch is skipped, and it
  supplies its own `__eq__` by exact quad-set equality (sound here since
  neither `original.py` nor the fixture uses blank nodes).

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.
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
    entry='testUpdateWithInitNs',
    calls=[_fresh_dataset],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
