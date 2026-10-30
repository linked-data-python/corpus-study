"""Validation driver for anuzzolese__pyrml__pyrml_pyrml_core.py__SPARQLSource_to_rdf.

`to_rdf` is an unbound method: it only needs `self` to carry `.endpoint`
and `.result_format`, and to itself be usable as the subject term (the
original passes `self` straight into `g.add((self, ...))`).

Two stand-ins for `self`:

* `FakeSPARQLSource`, a `URIRef` subclass with the two attributes (calls
  0-3);
* `TermMapLike`, closer to the real class: in pyrml, `SPARQLSource` ->
  `Source` -> `AbstractMap` -> `TermMap(IdentifiedNode)` (pyrml_api.py:63,
  309; pyrml_core.py:1912), i.e. an IdentifiedNode that is neither a URIRef
  nor a BNode, with `__eq__`/`__hash__` delegating to its `_id` (a URIRef,
  or a BNode when the map is anonymous), and whose `__init__` turns a truthy
  `endpoint`/`result_format` into a URIRef and a falsy one into None
  (pyrml_core.py:1914-1942).  ldpy's interpolation passes any rdflib `Node`
  through unchanged, so `{self}` is the very object `g.add` receives; these
  calls prove it on the real type.  Its `n3()` delegates to `_id` only so
  that the harness can canonicalise the graph (the real class inherits
  IdentifiedNode's NotImplementedError there): both sides get the same
  method, it decides nothing in the region.

Calls — each guard decides on its own, so each is taken alone:
  0. both attributes set (both `if` branches);
  1. neither (nothing beyond the type triple);
  2. endpoint only: kills a mutant that swaps the two guards or ties the
     result-format triple to `self.endpoint`;
  3. result_format only: the converse;
  4. TermMapLike with a URIRef id, both attributes given as str (coerced
     to URIRef by the real constructor);
  5. TermMapLike with a BNode id, endpoint only, result_format "" (falsy:
     the real constructor stores None).
"""
from rdflib import BNode, IdentifiedNode, Literal, URIRef

from rdfeval.harness import run_pair


class FakeSPARQLSource(URIRef):
    endpoint = None
    result_format = None


def _make(iri, endpoint=None, result_format=None):
    obj = FakeSPARQLSource(iri)
    obj.endpoint = endpoint
    obj.result_format = result_format
    return obj


class TermMapLike(IdentifiedNode):
    """TermMap's identity rules plus SPARQLSource's two attributes."""

    def __new__(cls, map_id, **kwargs):
        return IdentifiedNode.__new__(cls, map_id)

    def __init__(self, map_id, **kwargs):
        self._id = map_id if isinstance(map_id, IdentifiedNode) else URIRef(map_id)
        for key in ("endpoint", "result_format"):
            value = kwargs.get(key)
            setattr(self, "_" + key,
                    (value if isinstance(value, URIRef) else URIRef(value))
                    if value else None)

    endpoint = property(lambda self: self._endpoint)
    result_format = property(lambda self: self._result_format)

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, other):
        if isinstance(other, TermMapLike):
            return self._id == other._id
        return NotImplemented

    def n3(self, namespace_manager=None):
        return self._id.n3()


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
        lambda: ((_make("http://example.org/source3",
                        endpoint=URIRef("http://example.org/sparql3")),), {}),
        lambda: ((_make("http://example.org/source4",
                        result_format=URIRef("http://www.w3.org/ns/formats/SPARQL_Results_XML")),), {}),
        lambda: ((TermMapLike(
            URIRef("http://example.org/map/5"),
            endpoint="http://example.org/sparql5",
            result_format="http://www.w3.org/ns/formats/SPARQL_Results_JSON"),), {}),
        lambda: ((TermMapLike(BNode("src6"), endpoint="http://example.org/sparql6",
                              result_format=""),), {}),
    ],
)
