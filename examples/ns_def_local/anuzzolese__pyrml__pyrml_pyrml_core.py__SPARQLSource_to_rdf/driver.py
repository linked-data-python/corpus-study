"""Validation driver for anuzzolese__pyrml__pyrml_pyrml_core.py__SPARQLSource_to_rdf.

`to_rdf` is an unbound method: it only needs `self` to carry `.endpoint`
and `.result_format`, and to itself be usable as the subject term (the
original passes `self` straight into `g.add((self, ...))`, i.e. the real
`SPARQLSource` is an `IdentifiedNode`). A `URIRef` subclass with the two
extra attributes stands in for it.  Two calls: one with both optional
attributes set (covers the two `if` branches), one with neither (covers the
"nothing beyond the type triple" case).
"""
from rdflib import URIRef, Literal

from rdfeval.harness import run_pair


class FakeSPARQLSource(URIRef):
    endpoint = None
    result_format = None


def _make(iri, endpoint=None, result_format=None):
    obj = FakeSPARQLSource(iri)
    obj.endpoint = endpoint
    obj.result_format = result_format
    return obj


VERDICT = run_pair(
    __file__,
    entry='to_rdf',
    calls=[
        lambda: ((_make(
            "http://example.org/source1",
            endpoint=URIRef("http://example.org/sparql"),
            result_format=Literal("json"),
        ),), {}),
        lambda: ((_make("http://example.org/source2"),), {}),
    ],
)
