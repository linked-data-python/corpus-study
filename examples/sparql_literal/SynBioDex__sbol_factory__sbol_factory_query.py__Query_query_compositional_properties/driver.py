"""Validation driver for
SynBioDex__sbol_factory__sbol_factory_query.py__Query_query_compositional_properties.

`query_compositional_properties` is a reading region (design record
corpus/405): both its SELECTs read `self.graph` and it returns a plain list
of property IRIs (as strings), so the oracle is value equality against a
fixture graph, not graph isomorphism.

`self` is restored (AGENT_BATCH's ~163-regions case) as a `_Self`
stand-in exposing only the `.graph` attribute the region reads; its
`__eq__` always agrees, because `run_pair` also compares the arguments a
call was made with (to catch a region that mutates its input) and
`rdflib.Graph.__eq__` compares by `.identifier` -- a random blank node
unless one is given -- not by content, so a bare wrapper would fail that
comparison on every call for a reason that has nothing to do with whether
the translation is right (see the sibling note on
RDFLib/VocPrez/list_collections, the first region this was hit on).

`class_uri` is passed as a plain Python **string** at every real call site
in the upstream repository (verified directly against
SynBioDex/sbol_factory@5d01ec7f4c: `query_superclass`/`query_base_class`,
the functions that produce the values fed back into this one, both return
`str(row[0])`) -- not an `rdflib.URIRef`. That is exactly the case
`translated.ldpy`'s explicit `URIRef(class_uri)` exists for: ldpy's default
coercion turns a plain `str` interpolated into `s{ }` term position into a
`Literal`, not a `URIRef`, so leaving out the conversion would silently
change what the query matches. Passing a plain string here (rather than an
already-a-URIRef value that would paper over a missing conversion) is
deliberate.

`fixture.ttl` exercises all three ways a property can qualify -- a direct
`rdfs:domain`, a domain declared through `owl:unionOf` (the
`(owl:unionOf/rdf:rest*/rdf:first)*` hop of the FIRST query), and an
`owl:Restriction` reached through `rdfs:subClassOf` (the SECOND query) --
plus two neighbouring properties that must NOT match (wrong `rdf:type`,
missing `sbol:directlyComprises` sub-property). `_call(CLASS_A)` gets three
real solutions across the two queries; `_call(CLASS_Z)`, an isolated class,
is the zero-solution case for both queries at once. `list(set(...))` at the
end already makes the result order-independent, and no `ORDER BY` is
written anywhere: `ordered=False`.
"""
from pathlib import Path

from rdfeval.harness import run_pair, fixture_graph

_FIXTURE = Path(__file__).parent / "fixture.ttl"
_EX = "http://example.org/"


class _Self:
    """Stand-in for the real `Query` instance: carries only `.graph`, the
    one attribute this region reads. Never mutated by the call, so its
    identity is not an observable of the comparison -- the proof is the
    RETURN value, materialised and compared for real below."""

    def __init__(self, graph):
        self.graph = graph

    def __eq__(self, other):
        return True


def _call(class_uri):
    def build():
        return (_Self(graph=fixture_graph(_FIXTURE)), class_uri), {}
    return build


VERDICT = run_pair(
    __file__,
    entry="query_compositional_properties",
    fixture="fixture.ttl",
    calls=[
        _call(_EX + "ClassA"),
        _call(_EX + "ClassZ"),
    ],
    ordered=False,
)
