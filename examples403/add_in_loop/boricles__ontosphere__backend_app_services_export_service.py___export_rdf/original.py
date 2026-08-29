# Extracted from boricles/ontosphere@e055553268 : backend/app/services/export_service.py
# region: _export_rdf (lines 91-194, stratum add_in_loop)
# licence of the source repository: see meta.json
import logging
from context_shim import GraphData, GraphService, _resolve_uri
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
    if not namespace_uri.endswith("#") and not namespace_uri.endswith("/"):
        namespace_uri += "#"

    NS = Namespace(namespace_uri)

    g = Graph()
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("rdf", RDF)
    g.bind("xsd", XSD)
    g.bind("onto", NS)

    # -- Add an Ontology declaration --
    onto_uri = URIRef(namespace_uri.rstrip("#").rstrip("/"))
    g.add((onto_uri, RDF.type, OWL.Ontology))

    # -- Nodes --
    for node in graph_data.nodes:
        node_uri = _resolve_uri(node.uri, NS)

        if node.node_type == "class":
            g.add((node_uri, RDF.type, OWL.Class))
        elif node.node_type == "property":
            g.add((node_uri, RDF.type, OWL.ObjectProperty))
        elif node.node_type == "individual":
            g.add((node_uri, RDF.type, OWL.NamedIndividual))
        else:
            g.add((node_uri, RDF.type, OWL.Class))

        if node.label:
            g.add((node_uri, RDFS.label, Literal(node.label)))
        if node.description:
            g.add((node_uri, RDFS.comment, Literal(node.description)))

    # -- Edges --
    for edge in graph_data.edges:
        source = _resolve_uri(edge.source_uri, NS)
        target = _resolve_uri(edge.target_uri, NS)
        edge_type = edge.edge_type.upper()

        if edge_type == "SUBCLASS_OF":
            g.add((source, RDFS.subClassOf, target))
        elif edge_type == "DOMAIN":
            g.add((source, RDFS.domain, target))
        elif edge_type == "RANGE":
            # Check if target is an XSD datatype
            if edge.target_uri.startswith("xsd:"):
                datatype_name = edge.target_uri.split(":", 1)[1]
                g.add((source, RDFS.range, XSD[datatype_name]))
            else:
                g.add((source, RDFS.range, target))
        elif edge_type == "HAS_PROPERTY":
            g.add((source, OWL.hasKey, target))
        elif edge_type == "EQUIVALENT_TO":
            g.add((source, OWL.equivalentClass, target))
        elif edge_type == "RELATED_TO":
            # Generic relationship -- create an object property assertion
            rel_uri = _resolve_uri(edge.label or "relatedTo", NS)
            g.add((rel_uri, RDF.type, OWL.ObjectProperty))
            g.add((rel_uri, RDFS.domain, source))
            g.add((rel_uri, RDFS.range, target))
        elif edge_type == "DISJOINT_WITH":
            g.add((source, OWL.disjointWith, target))
        else:
            # Custom relationship type -- model as an object property
            rel_uri = _resolve_uri(edge.label or edge.edge_type, NS)
            g.add((rel_uri, RDF.type, OWL.ObjectProperty))
            if edge.label:
                g.add((rel_uri, RDFS.label, Literal(edge.label)))
            g.add((rel_uri, RDFS.domain, source))
            g.add((rel_uri, RDFS.range, target))

    # -- Serialise --
    format_map = {
        "owl": "xml",
        "ttl": "turtle",
        "jsonld": "json-ld",
    }
    rdf_format = format_map.get(fmt)
    if rdf_format is None:
        raise ValueError(
            f"Unsupported export format '{fmt}'. "
            f"Choose from: owl, ttl, jsonld, json"
        )

    serialised = g.serialize(format=rdf_format)

    logger.info(
        "Exported ontology %s as %s (%d bytes)",
        namespace_uri,
        fmt,
        len(serialised) if serialised else 0,
    )
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
