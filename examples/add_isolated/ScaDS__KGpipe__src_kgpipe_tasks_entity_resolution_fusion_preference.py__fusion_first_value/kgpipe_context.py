# Context shim (see meta.json): names fusion_first_value's region (lines
# 180-212 of preference.py) reaches as free variables from its enclosing
# function, from ScaDS/KGpipe@67ca171cf (src/kgpipe_tasks/entity_resolution/
# fusion/preference.py), reproduced or stood in so the region executes
# standalone:
#
#   - TrackRecord (source lines 20-26): the sibling pydantic model the
#     region appends to `selected`/`discarded`. Reproduced verbatim.
#   - TARGET_ONTOLOGY_NAMESPACE: imported in the real code from
#     kgpipe.common.config, an internal package of this same repository
#     (not installed as a library here). Its real value, copied verbatim
#     from src/kgpipe/common/config.py at the same commit, is
#     "http://kg.org/ontology/".
#   - canonicalize_entity_term / canonicalize_property_term (source lines
#     145-175): the region's own first two statements call these, but
#     their REAL bodies depend on entity_matches/relation_matches --
#     MatchCluster objects built by load_matches_from_file() from an
#     external match file this pair has no reason to fabricate, since
#     entity matching is not what this region does or what add_isolated
#     measures here. Reduced to the identity function: s_can/p_can end up
#     equal to s/p, exactly the outcome the real function already returns
#     for any term with no match (its own trailing `return term`) -- so the
#     region's own branches (allowed-predicate filter, rdf:type/namespace
#     filter, fusable vs. not, existing-value check) are exercised on graph
#     content the fixture controls directly.
#   - allowed_predicates / fusable_properties / is_fusable (source lines
#     127-131): the real sets are built from an ontology file loaded via
#     OntologyUtil.load_ontology_from_file(), an external file this pair
#     has no reason to fabricate either. Concrete, hand-picked predicates
#     replace them, chosen so the fixture routes through every branch: two
#     fusable predicates (rdf:type, one ordinary property) and one allowed
#     but non-fusable predicate (skos:altLabel -- allowed unconditionally
#     in the real set too, never added to the fusable one).
#   - build_fixture_graphs(): builds source_graph and seed_graph. A
#     function, not a module-level pair of Graph objects, so each side of
#     the pair gets ITS OWN fresh graphs -- see meta.json for why a shared
#     mutable Graph must never be imported from a shim.
#
# Identical bindings for both representations.
from rdflib import Graph, Literal, RDF, RDFS, SKOS, URIRef, XSD
from pydantic import BaseModel

EX = "http://kg.org/ontology/"
RES = "http://kg.org/resource/"
OTHER = "http://other.org/"

TARGET_ONTOLOGY_NAMESPACE = "http://kg.org/ontology/"


class TrackRecord(BaseModel):
    original_subject: str
    subject: str
    original_predicate: str
    predicate: str
    original_object: str
    object: str


def canonicalize_entity_term(term):
    return term


def canonicalize_property_term(term):
    return term


allowed_predicates = {
    str(RDF.type), str(RDFS.label), EX + "hasScore", str(SKOS.altLabel),
}
fusable_properties = {str(RDF.type), str(RDFS.label), EX + "hasScore"}


def is_fusable(p):
    return str(p) in fusable_properties


def build_fixture_graphs():
    """A fresh (source_graph, seed_graph) pair exercising every branch of
    the region -- see meta.json for the branch each triple routes through."""
    source_graph = Graph()
    seed_graph = Graph()

    alice = URIRef(RES + "Alice")
    bob = URIRef(RES + "Bob")
    carol = URIRef(RES + "Carol")
    dave = URIRef(RES + "Dave")
    eve = URIRef(RES + "Eve")

    # -- seed_graph: pre-existing values the fusion must not overwrite --
    seed_graph.add((bob, RDF.type, URIRef(EX + "OtherPersonType")))
    seed_graph.add((dave, RDFS.label, Literal("Existing Dave", lang="en")))
    seed_graph.add((eve, SKOS.altLabel, Literal("Dup", lang="en")))

    # -- source_graph: what fusion_first_value walks --
    # 1) rdf:type, object inside the target ontology namespace, no existing
    #    value in seed -> added.
    source_graph.add((alice, RDF.type, URIRef(EX + "Person")))
    # 2) rdf:type, but Bob already has one in seed_graph -> discarded.
    source_graph.add((bob, RDF.type, URIRef(EX + "Person")))
    # 3) rdf:type, object OUTSIDE the target ontology namespace -> skipped
    #    before the fusable/not-fusable split even runs (neighbourhood).
    source_graph.add((carol, RDF.type, URIRef(OTHER + "Thing")))
    # 4) predicate not in allowed_predicates at all -> skipped
    #    (neighbourhood).
    source_graph.add((alice, URIRef(EX + "secretCode"), Literal(42, datatype=XSD.integer)))
    # 5) ordinary fusable property, no existing value -> added.
    source_graph.add((alice, RDFS.label, Literal("Alice A.", lang="en")))
    # 6) ordinary fusable property, Dave already has one in seed -> discarded.
    source_graph.add((dave, RDFS.label, Literal("Dave D.", lang="en")))
    # 7) custom fusable property, no existing value -> added.
    source_graph.add((alice, URIRef(EX + "hasScore"), Literal(0.9, datatype=XSD.double)))
    # 8) allowed but NOT fusable -> copied unconditionally (not a dupe).
    source_graph.add((alice, SKOS.altLabel, Literal("Ally", lang="en")))
    # 9) allowed but NOT fusable, and this EXACT triple already sits in
    #    seed_graph -> the dedupe check skips it (zero triples added).
    source_graph.add((eve, SKOS.altLabel, Literal("Dup", lang="en")))

    return source_graph, seed_graph
