# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/shacl/generator.py
# region: ShapeGenerator._create_node_shape (lines 141-212, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
from .config import ShaclConfig, Severity, StrictnessLevel
from .converters import PropertyConstraint, get_converters_for_level
from .namespaces import SH, SHACL_PREFIXES

def _create_node_shape(self, cls: URIRef, converters: list) -> URIRef:
    """Create a NodeShape for a class.

    Args:
        cls: The class to create a shape for.
        converters: List of converters to apply.

    Returns:
        URI of the created shape.
    """
    shape_uri = URIRef(f"{self._shape_ns}{self._local_name(cls)}Shape")

    # Basic shape definition
    self.shapes_graph.add((shape_uri, RDF.type, SH.NodeShape))
    self.shapes_graph.add((shape_uri, SH.targetClass, cls))

    # Add name from rdfs:label if available
    if self.config.include_labels:
        label = self.source_graph.value(cls, RDFS.label)
        if label:
            self.shapes_graph.add((shape_uri, SH.name, Literal(str(label))))

    # Add description from rdfs:comment
    if self.config.include_descriptions:
        comment = self.source_graph.value(cls, RDFS.comment)
        if comment:
            self.shapes_graph.add((shape_uri, SH.description, Literal(str(comment))))

    # Collect all property constraints
    prop_constraints: dict[URIRef, PropertyConstraint] = {}

    # Apply each converter
    for converter in converters:
        constraints = converter.convert_for_class(cls, self.source_graph, self.config)

        for constraint in constraints:
            if constraint.path in prop_constraints:
                # Merge with existing constraint
                prop_constraints[constraint.path] = prop_constraints[constraint.path].merge(
                    constraint
                )
            else:
                prop_constraints[constraint.path] = constraint

    # Inherit constraints from superclasses if configured
    if self.config.inherit_constraints:
        inherited = self._get_inherited_constraints(cls, converters)
        for path, constraint in inherited.items():
            if path not in prop_constraints:
                prop_constraints[path] = constraint

    # Add property shapes, sorted by path for consistent output
    order = 1
    for path in sorted(prop_constraints.keys(), key=str):
        constraint = prop_constraints[path]
        constraint.order = order
        order += 1

        prop_shape = constraint.to_rdf(self.shapes_graph)
        self.shapes_graph.add((shape_uri, SH.property, prop_shape))

    # Handle closed shapes
    if self.config.closed and self.config.level == StrictnessLevel.STRICT:
        self.shapes_graph.add((shape_uri, SH.closed, Literal(True)))

        # Add ignored properties
        ignored = self._get_ignored_properties()
        if ignored:
            ignored_list = self._create_rdf_list(ignored)
            self.shapes_graph.add((shape_uri, SH.ignoredProperties, ignored_list))

    return shape_uri
