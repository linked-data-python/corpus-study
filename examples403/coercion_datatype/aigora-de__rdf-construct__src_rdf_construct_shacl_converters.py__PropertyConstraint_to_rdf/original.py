# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/shacl/converters.py
# region: PropertyConstraint.to_rdf (lines 88-141, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD
from .namespaces import SH

def to_rdf(self, shapes_graph: Graph) -> BNode:
    """Convert constraint to RDF representation.

    Creates a blank node with sh:property predicates.

    Args:
        shapes_graph: Graph to add triples to.

    Returns:
        Blank node representing the property shape.
    """
    prop_shape = BNode()

    shapes_graph.add((prop_shape, SH.path, self.path))

    if self.node_class:
        shapes_graph.add((prop_shape, SH["class"], self.node_class))

    if self.datatype:
        shapes_graph.add((prop_shape, SH.datatype, self.datatype))

    if self.min_count is not None:
        shapes_graph.add((prop_shape, SH.minCount, Literal(self.min_count)))

    if self.max_count is not None:
        shapes_graph.add((prop_shape, SH.maxCount, Literal(self.max_count)))

    if self.node_kind:
        shapes_graph.add((prop_shape, SH.nodeKind, self.node_kind))

    if self.name:
        shapes_graph.add((prop_shape, SH.name, Literal(self.name)))

    if self.description:
        shapes_graph.add((prop_shape, SH.description, Literal(self.description)))

    if self.in_values:
        # Create an RDF list for sh:in
        in_list = _create_rdf_list(shapes_graph, self.in_values)
        shapes_graph.add((prop_shape, SH["in"], in_list))

    if self.pattern:
        shapes_graph.add((prop_shape, SH.pattern, Literal(self.pattern)))

    if self.min_inclusive is not None:
        shapes_graph.add((prop_shape, SH.minInclusive, self.min_inclusive))

    if self.max_inclusive is not None:
        shapes_graph.add((prop_shape, SH.maxInclusive, self.max_inclusive))

    if self.order is not None:
        shapes_graph.add((prop_shape, SH.order, Literal(self.order)))

    return prop_shape
