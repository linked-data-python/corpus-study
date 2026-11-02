# Extracted from boricles/ontosphere@e055553268 : backend/app/services/export_service.py
# region: _export_rdf (lines 91-194, stratum add_in_loop)
# licence of the source repository: see meta.json
import logging
from context_shim import GraphData, _resolve_uri
logger = logging.getLogger(__name__)

def _export_rdf(
    graph_data: GraphData,
    fmt: str,
    namespace_uri: str,
) -> str:
    """Build an rdflib graph and serialise to the requested RDF format."""
    from rdflib import Graph, Literal, Namespace, URIRef
    from rdflib.namespace import OWL, RDF, RDFS, XSD

    # Ensure namespace ends with # or /
    if not namespace_uri.endswith(("#", "/")):
        namespace_uri += "#"

    NS = Namespace(namespace_uri)

    g = Graph()
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("rdf", RDF)
    g.bind("xsd", XSD)
    g.bind("onto", NS)

    # -- Add an Ontology declaration --
    g.add((URIRef(namespace_uri.rstrip("#").rstrip("/")), RDF.type, OWL.Ontology))

    # -- Nodes --
    node_types = {"property": OWL.ObjectProperty, "individual": OWL.NamedIndividual}
    for node in graph_data.nodes:
        node_uri = _resolve_uri(node.uri, NS)
        g.add((node_uri, RDF.type, node_types.get(node.node_type, OWL.Class)))
        if node.label:
            g.add((node_uri, RDFS.label, Literal(node.label)))
        if node.description:
            g.add((node_uri, RDFS.comment, Literal(node.description)))

    # -- Edges --
    predicates = {
        "SUBCLASS_OF": RDFS.subClassOf,
        "DOMAIN": RDFS.domain,
        "RANGE": RDFS.range,
        "HAS_PROPERTY": OWL.hasKey,
        "EQUIVALENT_TO": OWL.equivalentClass,
        "DISJOINT_WITH": OWL.disjointWith,
    }
    for edge in graph_data.edges:
        source = _resolve_uri(edge.source_uri, NS)
        target = _resolve_uri(edge.target_uri, NS)
        edge_type = edge.edge_type.upper()

        # Check if target is an XSD datatype
        if edge_type == "RANGE" and edge.target_uri.startswith("xsd:"):
            target = XSD[edge.target_uri.split(":", 1)[1]]
        if edge_type in predicates:
            g.add((source, predicates[edge_type], target))
        else:
            # Generic relationship -- create an object property assertion
            # Custom relationship type -- model as an object property
            related_to = edge_type == "RELATED_TO"
            rel_uri = _resolve_uri(
                edge.label or ("relatedTo" if related_to else edge.edge_type), NS)
            g += [(rel_uri, RDF.type, OWL.ObjectProperty),
                  (rel_uri, RDFS.domain, source),
                  (rel_uri, RDFS.range, target)]
            if edge.label and not related_to:
                g.add((rel_uri, RDFS.label, Literal(edge.label)))

    # -- Serialise --
    rdf_format = {"owl": "xml", "ttl": "turtle", "jsonld": "json-ld"}.get(fmt)
    if rdf_format is None:
        raise ValueError(f"Unsupported export format '{fmt}'. Choose from: owl, ttl, jsonld, json")

    serialised = g.serialize(format=rdf_format)

    logger.info("Exported ontology %s as %s (%d bytes)", namespace_uri, fmt, len(serialised))
    return serialised


# Demo harness (identical on both sides, see meta.json): _export_rdf's graph
# never escapes the function except serialised to text, and rdflib's
# serialisers are not byte-stable across two independently built (even if
# isomorphic) graphs -- comparing the returned string with plain equality
# would be comparing serialisation order, not RDF content, which is exactly
# what run_pair's docstring says graph comparison must not do ("never raw
# serialisation"). This round-trips the string back into a fresh Graph with
# the same fmt -> rdf_format mapping _export_rdf itself uses, so the driver
# compares the two GRAPHS by isomorphism instead.
def demo(graph_data, fmt, namespace_uri):
    from rdflib import Graph
    serialised = _export_rdf(graph_data, fmt, namespace_uri)
    rdf_format = {"owl": "xml", "ttl": "turtle", "jsonld": "json-ld"}[fmt]
    g = Graph()
    g.parse(data=serialised, format=rdf_format)
    return g
