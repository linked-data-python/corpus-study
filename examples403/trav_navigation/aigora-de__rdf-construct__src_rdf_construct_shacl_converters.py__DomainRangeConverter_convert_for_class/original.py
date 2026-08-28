# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/shacl/converters.py
# region: DomainRangeConverter.convert_for_class (lines 245-283, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef, XSD

def convert_for_class(
    self,
    cls: URIRef,
    source_graph: Graph,
    config: "ShaclConfig",
) -> list[PropertyConstraint]:
    """Find properties with domain of this class and create constraints."""
    constraints: list[PropertyConstraint] = []

    # Find all properties with this class as domain
    for prop in source_graph.subjects(RDFS.domain, cls):
        if not isinstance(prop, URIRef):
            continue

        constraint = PropertyConstraint(path=prop)

        # Get range if defined
        range_value = source_graph.value(prop, RDFS.range)
        if range_value:
            if self._is_datatype(range_value, source_graph):
                constraint.datatype = range_value
            else:
                constraint.node_class = range_value

        # Add label as name if configured
        if config.include_labels:
            label = source_graph.value(prop, RDFS.label)
            if label:
                constraint.name = str(label)

        # Add comment as description if configured
        if config.include_descriptions:
            comment = source_graph.value(prop, RDFS.comment)
            if comment:
                constraint.description = str(comment)

        constraints.append(constraint)

    return constraints
