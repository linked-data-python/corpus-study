"""Validation driver for kumagallium__asterism__api_tests_test_crosswalk_api.py___seed_promoted.

_seed_promoted has no graph_read at all (see meta.json categories): it
blindly writes `rows` into a freshly-obtained named graph, then a
control-graph status triple, then a registry meta.json file. meta.oracle is
"values" per the pipeline's classification, but the equivalence this region
is actually about is a WRITE (a mutated argument), not a read. run_pair
compares every positional argument after the call, and for a plain
`rdflib.Graph` that comparison is isomorphism -- but `rdflib.Dataset` IS a
`Graph` (a ConjunctiveGraph subclass) too, and `rdfeval.harness.
graphs_isomorphic` -> `rdflib.compare.to_isomorphic` breaks on it: it
iterates the dataset as quads (s, p, o, context) and rdflib.compare expects
plain triples. That is a harness limitation (rdfeval/ is out of scope for
this batch, so it cannot be patched here), confirmed empirically: passing a
real `rdflib.Dataset` as call[0] makes run_pair itself raise
"ValueError: too many values to unpack (expected 3)" inside to_isomorphic.

The workaround lives entirely in this driver: `_FakeDataset` duck-types the
two methods `_seed_promoted` actually calls (`.graph(iri)`, `.update(query)`)
over a real `rdflib.Dataset` it holds internally, but is not itself a `Graph`
subclass -- so run_pair's automatic argument comparison falls through to
plain `==`, which `_FakeDataset.__eq__` implements as an exact quad-set
comparison. This region produces no blank nodes at all (every term is a
`URIRef` built from a plain string, or a `Literal`), so exact quad-set
equality is exactly as strong as isomorphism would have been here -- no
bnode abstraction is needed.

The registry meta.json the region writes is compared too: each `_FakeDataset`
owns its own fresh `registry` directory (created per side, since the call
factory runs once per side), `_make_call` passes that directory as
registry_root, and `__eq__` compares, besides the quads, every file under it
(relative path and exact bytes). A mutated meta.json field (`promoted`,
`name`, `status`, ...) is therefore a diff, not an unobserved effect.

Calls exercised:
  1. the real call shape of the repository (`"ds-a"`, one row `("urn:a1",
     "Bi₂Te₃")`) plus a second, ASCII row -- several solutions, with the
     neighbouring graph ds-other that must stay intact;
  2. the degenerate row values the `+{ }` write must not drop or coerce
     away: the empty string `""`, the integer `0`, the float `1.5`, and a
     duplicate of an earlier row (a set of quads absorbs it);
  3. zero rows: the control triple and meta.json are still written, no
     triple goes into the key graph.
"""
import atexit
import shutil
import tempfile
from pathlib import Path

import rdflib

from rdfeval.harness import run_pair, fixture_graph

_HERE = Path(__file__).resolve().parent
# every registry of this run lives under one temp directory, removed at exit
_TMP = tempfile.mkdtemp(prefix="rdfeval-seed-promoted-")
atexit.register(shutil.rmtree, _TMP, True)
_OTHER_CANONICAL = rdflib.URIRef(
    "https://kumagallium.github.io/asterism/graph/canonical/ds-other"
)


class _RegistryRoot(type(Path())):
    """A registry directory whose location is not part of the comparison:
    two sides use two different temp directories, so plain Path equality
    would be a false diff. Its *content* is compared by `_FakeDataset.__eq__`."""

    def __eq__(self, other):
        # same name only: Path.mkdir(parents=True) compares a path with its parent
        return isinstance(other, _RegistryRoot) and self.name == other.name

    __hash__ = type(Path()).__hash__


class _FakeDataset:
    """See module docstring: duck-typed so run_pair's own argument-equality
    check does not hit the Dataset/to_isomorphic harness limitation."""

    def __init__(self):
        self._ds = rdflib.Dataset()
        # a fresh registry per instance, hence per side
        self.registry = _RegistryRoot(tempfile.mkdtemp(dir=_TMP), "registry")

    def _files(self):
        if not self.registry.exists():
            return {}
        return {str(f.relative_to(self.registry)): f.read_bytes()
                for f in sorted(self.registry.rglob("*")) if f.is_file()}

    def graph(self, identifier):
        return self._ds.graph(identifier)

    def update(self, query):
        self._ds.update(query)

    def _quads(self):
        return {(str(g.identifier), s, p, o)
                for g in self._ds.contexts()
                for s, p, o in g}

    def __eq__(self, other):
        if not isinstance(other, _FakeDataset):
            return NotImplemented
        return (self._quads() == other._quads()
                and self._files() == other._files())

    def __repr__(self):
        return (f"_FakeDataset({sorted(self._quads())!r}, "
                f"files={self._files()!r})")


def _make_call(rows, dataset_id="ds-a"):
    def call():
        ds = _FakeDataset()
        neighbour = fixture_graph(_HERE / "fixture.ttl")
        other_g = ds.graph(_OTHER_CANONICAL)
        for t in neighbour:
            other_g.add(t)
        return (ds, ds.registry, dataset_id, list(rows)), {}
    return call


# several solutions, including a non-ASCII value (as in the real test
# suite's own call: _seed_promoted(ds, ..., "ds-a", [("urn:a1", "Bi₂Te₃")]))
_ROWS = [("urn:a1", "Bi₂Te₃"), ("urn:a2", "Bi2Te3")]
# empty string, 0, a float, and a duplicate of an earlier row
_DEGENERATE_ROWS = [("urn:a3", ""), ("urn:a4", 0), ("urn:a6", 1.5),
                    ("urn:a3", "")]


VERDICT = run_pair(
    __file__,
    entry="_seed_promoted",
    fixture="fixture.ttl",
    calls=[_make_call(_ROWS), _make_call(_DEGENERATE_ROWS, "ds-b"),
           _make_call([], "ds-c")],
)
