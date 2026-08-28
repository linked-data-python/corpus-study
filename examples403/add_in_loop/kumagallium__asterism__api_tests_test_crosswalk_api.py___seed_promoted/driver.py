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

registry_root is a single shared Path (not re-randomised per call), so the
plain-value comparison of call[0].arg[1] does not become a false diff over
two unrelated temp directories -- only the RDF content is what this
region's semantics are about; the registry meta.json filesystem side effect
is exercised (both sides really write it) but not compared.
"""
import tempfile
from pathlib import Path

import rdflib

from rdfeval.harness import run_pair, fixture_graph

_HERE = Path(__file__).resolve().parent
_REGISTRY_ROOT = Path(tempfile.mkdtemp(prefix="rdfeval-seed-promoted-")) / "registry"
_OTHER_CANONICAL = rdflib.URIRef(
    "https://kumagallium.github.io/asterism/graph/canonical/ds-other"
)


class _FakeDataset:
    """See module docstring: duck-typed so run_pair's own argument-equality
    check does not hit the Dataset/to_isomorphic harness limitation."""

    def __init__(self):
        self._ds = rdflib.Dataset()

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
        return self._quads() == other._quads()

    def __repr__(self):
        return f"_FakeDataset({sorted(self._quads())!r})"


def _make_call():
    ds = _FakeDataset()
    neighbour = fixture_graph(_HERE / "fixture.ttl")
    other_g = ds.graph(_OTHER_CANONICAL)
    for t in neighbour:
        other_g.add(t)
    # several solutions, including a non-ASCII value (as in the real test
    # suite's own call: _seed_promoted(ds, ..., "ds-a", [("urn:a1", "Bi₂Te₃")]))
    rows = [("urn:a1", "Bi₂Te₃"), ("urn:a2", "Bi2Te3")]
    return (ds, _REGISTRY_ROOT, "ds-a", rows), {}


VERDICT = run_pair(
    __file__,
    entry="_seed_promoted",
    fixture="fixture.ttl",
    calls=[_make_call],
)
