"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_shacl2flink_lib_shacl_properties_to_sql.py__inverse_relationship_predicate.

`inverse_relationship_predicate(g, path)` only reads `g` (it neither builds
nor mutates a graph), and `meta.oracle` is "isomorphism" rather than
"values" -- per AGENT_BATCH.md this is a function region, so the driver
supplies call arguments directly instead of a shared fixture.ttl (same
pattern as the `translate` precedent in stratum bind_initbindings, same
repository/commit).

Each case below builds its own two-hop `sh:path ( ... )` rdf:List with
`rdflib.collection.Collection` -- the shape `path` names -- as a FRESH
graph per call (a callable case, not a shared tuple: `run_pair` invokes it
once per side, so mutating one side's graph cannot leak into the other's).

To avoid a hollow green (a `bool`-like reader that only ever sees the
"nothing matches" branch), the cases below cover: the canonical shape
(returns the predicate), a first hop whose sh:inversePath is not
ngsi-ld:hasObject, a list that is not exactly two steps long, a second hop
with no sh:inversePath at all (plus a neighbouring unrelated triple on
that same node, to prove the read does not match on it), and a second hop
whose sh:inversePath is itself a blank node (the nested-expression case
the docstring calls out by name).
"""
from rdflib import BNode, Graph, URIRef
from rdflib.collection import Collection
from rdflib.namespace import SH, Namespace

from rdfeval.harness import run_pair

NGSILD = Namespace("https://uri.etsi.org/ngsi-ld/")
EX = Namespace("http://example.org/")


def _canonical():
    # sh:path ( [ sh:inversePath ngsi-ld:hasObject ] [ sh:inversePath ex:hasCartridge ] )
    g = Graph()
    step1, step2 = BNode(), BNode()
    g.add((step1, SH.inversePath, NGSILD.hasObject))
    g.add((step2, SH.inversePath, EX.hasCartridge))
    path = BNode()
    Collection(g, path, [step1, step2])
    return (g, path), {}


def _wrong_first_hop():
    # first hop does not walk back out through ngsi-ld:hasObject -> None
    g = Graph()
    step1, step2 = BNode(), BNode()
    g.add((step1, SH.inversePath, EX.somethingElse))
    g.add((step2, SH.inversePath, EX.hasCartridge))
    path = BNode()
    Collection(g, path, [step1, step2])
    return (g, path), {}


def _wrong_length():
    # a bare one-hop inverse (no second step) -> None
    g = Graph()
    step1 = BNode()
    g.add((step1, SH.inversePath, NGSILD.hasObject))
    path = BNode()
    Collection(g, path, [step1])
    return (g, path), {}


def _second_hop_missing():
    # second hop has no sh:inversePath at all -> None; the unrelated triple
    # on step2 is neighbourhood that must not make the pattern match.
    g = Graph()
    step1, step2 = BNode(), BNode()
    g.add((step1, SH.inversePath, NGSILD.hasObject))
    g.add((step2, EX.unrelatedPredicate, EX.someValue))
    path = BNode()
    Collection(g, path, [step1, step2])
    return (g, path), {}


def _second_hop_is_bnode():
    # second hop's sh:inversePath is a nested expression (a blank node),
    # not a plain predicate -> None, per the docstring's own example.
    g = Graph()
    step1, step2, nested = BNode(), BNode(), BNode()
    g.add((step1, SH.inversePath, NGSILD.hasObject))
    g.add((step2, SH.inversePath, nested))
    path = BNode()
    Collection(g, path, [step1, step2])
    return (g, path), {}


VERDICT = run_pair(
    __file__,
    entry="inverse_relationship_predicate",
    calls=[_canonical, _wrong_first_hop, _wrong_length,
           _second_hop_missing, _second_hop_is_bnode],
)
