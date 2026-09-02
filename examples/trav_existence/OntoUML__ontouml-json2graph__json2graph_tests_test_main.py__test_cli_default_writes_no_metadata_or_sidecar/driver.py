"""Validation driver for OntoUML__ontouml-json2graph__json2graph_tests_test_main.py__test_cli_default_writes_no_metadata_or_sidecar.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). The graph is not passed in directly, though: the region writes
it itself by shelling out to a CLI (`write_cardinality_project` +
`run_metadata_cli`, stubbed in context_shim.py -- see meta.json). The driver
controls what that stub produces by dropping a `_use_prov_fixture` marker
file into the tmp_path it hands the region beforehand: absent, the stub
copies fixture.ttl (metadata-free, the upstream test's own scenario);
present, it copies fixture_with_prov.ttl (a prov:Entity triple added).

`entry` is the `demo` harness both files carry identically (see meta.json):
the region is a pytest test that only ever asserts, so `demo` turns a
failed assertion into a comparable value instead of letting it abort the
driver -- otherwise the FALSE side of `bool(m{ })` (the only one the real
upstream test exercises) would be all the oracle could ever see.
"""
import tempfile
from pathlib import Path

from rdfeval.harness import run_pair


def _case(with_prov: bool):
    # tmp_path is created ONCE per case, shared by both the original and the
    # translated call: both write the identical content to it (the shim is
    # deterministic given the marker file), so nothing leaks meaningfully,
    # and a shared path lets `run_pair`'s argument comparison see the same
    # value on both sides instead of two different temp directories.
    tmp_path = Path(tempfile.mkdtemp())
    if with_prov:
        (tmp_path / "_use_prov_fixture").touch()

    def make():
        return (tmp_path,), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        _case(with_prov=False),  # metadata-free output -> assertion passes ("ok")
        _case(with_prov=True),   # prov:Entity present -> assertion fails
    ],
)
