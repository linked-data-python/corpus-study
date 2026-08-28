"""Validation driver for kumagallium__asterism__api_tests_test_crosswalk_api.py___seed_promoted.

_seed_promoted has no graph_read at all (see meta.json categories): it
blindly writes `rows` into a freshly-obtained named graph, then a
control-graph status triple, then a registry meta.json file. meta.oracle is
"values" per the pipeline's classification, but the equivalence this region
is actually about is a WRITE (a mutated argument), not a read -- and
`rdflib.Dataset` is itself an `rdflib.Graph` (a ConjunctiveGraph subclass),
so passing it as call[0] makes run_pair's own per-argument comparison
isomorphism-check it automatically. That keeps the driver inside the
fixture= contract the "values" oracle expects (fixture.ttl still supplies
pre-existing "neighbourhood" content this call must leave untouched -- see
fixture.ttl), while proving the thing that actually matters here: the RDF
this call adds to `ds` is the same on both sides.

registry_root is a single shared Path (not re-randomised per call), so the
plain-value comparison of call[0].arg[1] does not become a false diff over
two unrelated temp directories -- only the Dataset argument's RDF content is
what this region's semantics are about; the registry meta.json filesystem
side effect is exercised (both sides really write it) but not compared.
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


def _make_call():
    ds = rdflib.Dataset()
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
