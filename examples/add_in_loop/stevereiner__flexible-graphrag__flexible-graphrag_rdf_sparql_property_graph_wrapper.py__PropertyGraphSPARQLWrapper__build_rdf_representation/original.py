# Extracted from stevereiner/flexible-graphrag@7d885d5379 : flexible-graphrag/rdf/sparql_property_graph_wrapper.py
# region: PropertyGraphSPARQLWrapper._build_rdf_representation (lines 26-69, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal as RDFLiteral, Namespace
from rdflib.namespace import RDF, RDFS

def _build_rdf_representation(self) -> None:
    """Convert property graph to RDF for SPARQL querying"""

    # Define namespaces
    PG = Namespace("http://example.org/property-graph/")

    # Get all nodes from property graph
    nodes = self.graph_store.get_nodes()  # Implementation depends on store

    for node in nodes:
        node_uri = URIRef(f"{PG}{node.id}")

        # Add node with its label as type
        label = getattr(node, "label", None) or getattr(node, "labels", None)
        if label:
            if isinstance(label, (list, set, tuple)):
                for l in label:
                    self.rdf_graph.add((node_uri, RDF.type, URIRef(f"{PG}{l}")))
            else:
                self.rdf_graph.add((node_uri, RDF.type, URIRef(f"{PG}{label}")))

        # Add node properties
        properties = getattr(node, "properties", {}) or getattr(node, "metadata", {})
        for prop_name, prop_value in properties.items():
            prop_uri = URIRef(f"{PG}{prop_name}")
            value = RDFLiteral(str(prop_value))
            self.rdf_graph.add((node_uri, prop_uri, value))

    # Get all relationships
    relations = self.graph_store.get_relations()  # Implementation depends on store

    for relation in relations:
        source_uri = URIRef(f"{PG}{relation.source_id}")
        target_uri = URIRef(f"{PG}{relation.target_id}")
        rel_uri = URIRef(f"{PG}{relation.label}")

        self.rdf_graph.add((source_uri, rel_uri, target_uri))

        # Add relation properties if any
        rel_props = getattr(relation, "properties", {})
        for prop_name, prop_value in rel_props.items():
            prop_uri = URIRef(f"{PG}{relation.label}_{prop_name}")
            value = RDFLiteral(str(prop_value))
            self.rdf_graph.add((source_uri, prop_uri, value))
