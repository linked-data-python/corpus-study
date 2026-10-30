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

Repair pass (2026-10-30).  The two neighbours above each broke two
constraints at once, so five mutants stayed green (rdf:type dropped from
either query, rdfs:subPropertyOf or owl:onProperty dropped from the second,
rdf:rest* reduced to rdf:rest).  fixture.ttl now carries, for EACH triple
pattern of EACH query, a neighbour that breaks only that pattern -- once
with the object changed (owl:DatatypeProperty, sbol:otherRelation, a
restriction of ex:ClassB...) and once with the predicate changed
(rdfs:seeAlso, rdfs:range, owl:intersectionOf, owl:equivalentClass,
owl:someValuesFrom) -- plus three more shapes of the union list (ex:ClassA
first, third, nested), and ex:comprisesBoth, found by both queries, which
only the final list(set(...)) deduplicates.  A third call, ex:ClassB, has
its own positive cases in both queries (ex:onlyB, ex:q2OnlyB) so the
neighbours of ex:ClassA are not red herrings.

The graph is bound to the prefixes the repository binds on Query.graph
(query.py:23-28: sbol, rdfs, rdf; owl is an rdflib default): the original's
query text uses them unresolved, and resolves them through the graph's
namespace manager, while the translation declares them by @prefix.

`_Self.__eq__` compares the two graphs by isomorphism (the region must not
mutate them), not "always equal" as before.  The driver also checks that
rdflib's global CUSTOM_EVALS registry is empty: the repository registers a
custom evaluator only in custom_eval.py under __main__, and a registry
shared by the two sides would make them run the same evaluator.
"""
from pathlib import Path

import rdflib.plugins.sparql
from rdflib import URIRef

from rdfeval.harness import fixture_graph, graphs_isomorphic, run_pair

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
        return isinstance(other, _Self) and graphs_isomorphic(self.graph, other.graph)

    __hash__ = None


def _graph():
    """The fixture, bound to the prefixes Query.__init__ binds (query.py:23-28)."""
    g = fixture_graph(_FIXTURE)
    g.namespace_manager.bind('sbol', URIRef('http://sbols.org/v3#'))
    g.namespace_manager.bind('rdfs', URIRef('http://www.w3.org/2000/01/rdf-schema#'))
    g.namespace_manager.bind('rdf', URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#'))
    return g


def _call(class_uri):
    def build():
        return (_Self(graph=_graph()), class_uri), {}
    return build


if rdflib.plugins.sparql.CUSTOM_EVALS:
    raise RuntimeError("rdflib CUSTOM_EVALS is not empty: "
                       f"{sorted(rdflib.plugins.sparql.CUSTOM_EVALS)}")

VERDICT = run_pair(
    __file__,
    entry="query_compositional_properties",
    fixture="fixture.ttl",
    calls=[
        _call(_EX + "ClassA"),
        _call(_EX + "ClassZ"),
        _call(_EX + "ClassB"),
    ],
    ordered=False,
)
