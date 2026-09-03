"""Validation driver for OntoUML__ontouml-json2graph__json2graph_tests_test_main.py__test_empty_text_shape_value_is_omitted_without_warning.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405). The graph is not passed in directly, though: the region builds
it itself by calling the package's own JSON->RDF decoder
(`write_text_shape_project` + `decode_ontouml_json2graph`, stubbed in
context_shim.py -- see meta.json). The driver controls what that stub
produces by dropping a `_fixture_name` marker file into the tmp_path it hands
the region beforehand, naming which of the four Turtle fixtures alongside
this file to copy in as `ontouml_graph`.

`entry` is the `demo` harness both files carry identically (see meta.json):
the region is a pytest test that only ever asserts, so `demo` turns a
failed assertion into a comparable value instead of letting it abort the
driver -- otherwise only the TRUE side of all three `bool(m{ })` checks
(the only one the real upstream test exercises) would ever be observable.
"""
import tempfile
from pathlib import Path

from rdfeval.harness import run_pair


def _case(fixture_name: str):
    # tmp_path is created ONCE per case, shared by both the original and the
    # translated call: both write the identical content to it (the shim is
    # deterministic given the marker file), so nothing leaks meaningfully,
    # and a shared path lets `run_pair`'s argument comparison see the same
    # value on both sides instead of two different temp directories.
    tmp_path = Path(tempfile.mkdtemp())
    (tmp_path / "_fixture_name").write_text(fixture_name, encoding="utf-8")

    def make():
        return (tmp_path,), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        _case("fixture_clean.ttl"),          # type present, no leftovers -> "ok"
        _case("fixture_missing_type.ttl"),   # no rdf:type Text -> assert 1 fails
        _case("fixture_leftover_text.ttl"),  # leftover ontouml:text -> assert 2 fails
        _case("fixture_leftover_value.ttl"), # leftover ontouml:value -> assert 3 fails
    ],
)
