"""Validation driver for boricles__ontosphere__backend_app_services_export_service.py___export_rdf.

Establishes semantic equivalence of original.py and translated.ldpy via the
demo(graph_data, fmt, namespace_uri) harness both files carry (see
meta.json): it calls _export_rdf, then round-trips the returned RDF text
back into a fresh Graph, so the driver compares two GRAPHS by isomorphism
rather than two serialised strings (rdflib's serialisers are not byte-stable
across independently built, even isomorphic, graphs).

CALL_1 -- namespace_uri without a trailing "#"/"/" (the auto-append branch),
four nodes covering every node_type branch (class / property / individual /
an unrecognised type that falls through to the "else: owl:Class" default)
and every combination of label/description present-vs-empty-string (the
add-in-loop joker: `if node.label:` / `if node.description:` become
unbound-variable drops in `+{ }`), plus one node with an absolute
"http://..." uri (the other branch of _resolve_uri). Twelve edges covering
every edge_type branch: SUBCLASS_OF, DOMAIN, RANGE with an "xsd:" target
(the XSD[...] lookup) and RANGE without one, HAS_PROPERTY, EQUIVALENT_TO,
RELATED_TO with a label and RELATED_TO falling back to "relatedTo",
DISJOINT_WITH, a custom type with a label and one without (the second
add-in-loop joker, on rdfs:label in the "else" branch), and one edge with
absolute "http://..." source/target uris. edge_type is given in mixed case
to confirm `.upper()` still runs unchanged.

CALL_2 -- namespace_uri already ending in "/" (no auto-append), and an
EMPTY GraphData (no nodes, no edges): both add-in-loop loops run zero
iterations, so the only triple in the graph must be the Ontology
declaration -- the "loop contributes nothing when there is nothing to loop
over" case.

CALL_3 -- fmt="owl" (RDF/XML) instead of "ttl", exercising the other
branch of the format_map dispatch and a different serialiser/parser pair
for the round trip, with a small node/edge set.
"""
from rdfeval.harness import run_pair
from context_shim import GraphData, GraphNode, GraphEdge

NODES_1 = [
    GraphNode(uri="Person", label="", description="", node_type="class"),
    GraphNode(uri="worksAt", label="Works At", description="",
              node_type="property"),
    GraphNode(uri="alice", label="", description="An individual named Alice",
              node_type="individual"),
    GraphNode(uri="http://external.org/Thing", label="External Thing",
              description="from another ontology", node_type="weird"),
]

EDGES_1 = [
    GraphEdge(source_uri="n1", target_uri="n2", edge_type="subclass_of"),
    GraphEdge(source_uri="n2", target_uri="n3", edge_type="DOMAIN"),
    GraphEdge(source_uri="n3", target_uri="xsd:integer", edge_type="RANGE"),
    GraphEdge(source_uri="n1", target_uri="n4", edge_type="range"),
    GraphEdge(source_uri="n2", target_uri="n3", edge_type="has_property"),
    GraphEdge(source_uri="n1", target_uri="n3", edge_type="EQUIVALENT_TO"),
    GraphEdge(source_uri="n1", target_uri="n2", edge_type="related_to",
              label="knows"),
    GraphEdge(source_uri="n2", target_uri="n4", edge_type="RELATED_TO",
              label=""),
    GraphEdge(source_uri="n3", target_uri="n4", edge_type="disjoint_with"),
    GraphEdge(source_uri="n1", target_uri="n2", edge_type="customType",
              label="customLabel"),
    GraphEdge(source_uri="n2", target_uri="n1", edge_type="anotherCustom",
              label=""),
    GraphEdge(source_uri="http://external.org/A",
              target_uri="http://external.org/B", edge_type="subclass_of"),
]

CALL_1 = (
    (GraphData(nodes=NODES_1, edges=EDGES_1), "ttl", "http://example.org/onto"),
    {},
)

CALL_2 = (
    (GraphData(nodes=[], edges=[]), "ttl", "http://example.org/onto2/"),
    {},
)

NODES_3 = [
    GraphNode(uri="Widget", label="Widget", description="A small part",
              node_type="class"),
]
EDGES_3 = [
    GraphEdge(source_uri="Widget", target_uri="xsd:string", edge_type="RANGE"),
]
CALL_3 = (
    (GraphData(nodes=NODES_3, edges=EDGES_3), "owl", "http://example.org/onto3#"),
    {},
)

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[CALL_1, CALL_2, CALL_3],
)
