"""Validation driver for cognitedata__neat__cognite_neat__v0_core__instances_transformers__classic_cdf.py__RelationshipAsEdgeTransformer__relationship_as_edge.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`_relationship_as_edge` is a method (`self, graph, ...`); `self` only needs
`_namespace`, `_NOT_PROPERTIES`, `_predicate` and `_create_edge` -- see
context_shim.py.  A single, stateless receiver instance is reused for every
call on both sides (a fresh instance per side would fail the harness's
default ``==`` for a reason unrelated to translation correctness).

`lookup_entity_with_external_id` is the last positional argument: a small
in-memory lookup over the fixture's Asset/TimeSeries entities, faithful to
what `RelationshipAsEdgeTransformer.create_lookup_entity_with_external_id`
does against a real graph (SELECT the entity by rdf:type and externalId),
raising ValueError when nothing matches -- exactly the case the region
catches to warn and return [].

Three calls exercise: (1) a relationship with all properties resolvable --
an edge is built; (2) a relationship whose *source* external id is not a
known Asset -- ValueError on the first lookup, warns, returns []; (3) a
relationship whose *target* external id is not known -- warns on the second
lookup, returns [].  Warnings go through the `warnings` module, not stdout,
so they are not part of what the harness compares; the observable behaviour
is the returned edge triple list, which the zero-solution calls (2) and (3)
exercise as the "nothing found" case.
"""
from rdflib import Namespace, URIRef

from rdfeval.harness import run_pair, fixture_graph
from context_shim import RelationshipAsEdgeTransformer

NS = Namespace("http://example.org/classic/")
_RECEIVER = RelationshipAsEdgeTransformer(NS)


def _lookup(entity_type, external_id):
    known = {
        ("Asset", "asset-1"): URIRef(NS["asset-1"]),
        ("TimeSeries", "ts-1"): URIRef(NS["ts-1"]),
    }
    key = (entity_type, external_id)
    if key in known:
        return known[key]
    raise ValueError(f"no {entity_type} with externalId {external_id!r}")


def _case(relationship_id, source_type, target_type):
    from pathlib import Path

    fixture = Path(__file__).resolve().parent / "fixture.ttl"
    return lambda: (
        (_RECEIVER, fixture_graph(fixture), URIRef(relationship_id), source_type, target_type, _lookup),
        {},
    )


VERDICT = run_pair(
    __file__,
    entry="_relationship_as_edge",
    fixture="fixture.ttl",
    calls=[
        # both endpoints resolve: an edge is built
        _case("http://example.org/classic/rel-1", "Asset", "TimeSeries"),
        # source externalId not found -> warns, returns []
        _case("http://example.org/classic/rel-2", "Asset", "TimeSeries"),
        # target externalId not found -> warns, returns []
        _case("http://example.org/classic/rel-3", "Asset", "TimeSeries"),
    ],
)
