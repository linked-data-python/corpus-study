# Extracted from lazlop/semantic_objects@243c5efd8c : src/semantic_objects/exporters.py
# region: RdfExporter._create_qualified_value_shape (lines 318-371, stratum add_isolated)
# licence of the source repository: see meta.json
from dataclasses import _MISSING_TYPE
from .namespaces import PARAM, RDF, RDFS, SH, XSD, bind_prefixes
from rdflib import Graph, Literal, BNode, URIRef

@staticmethod
def _create_qualified_value_shape(cls, g, prop_node, field_obj, field_name, class_iri):
    """Create a qualified value shape for a field"""
    members = RdfExporter._unwrap_field_type_members(cls, field_obj)
    if len(members) > 1:
        # A qualified Union field sharing one path (e.g. FiberOpticCable's
        # medium alternation) - the qualifiedValueShape's own value is
        # itself an sh:or of per-member value shapes, matching how the
        # vendored ontology structures this variant of the pattern.
        qual_val_shape = BNode()
        g.add((qual_val_shape, SH['or'],
               _rdf_list(g, [RdfExporter._value_shape_for_type(g, m) for m in members])))
        g.add((qual_val_shape, RDF.type, SH.NodeShape))
        g.add((prop_node, SH.qualifiedMinCount, Literal(field_obj.metadata.get('min') or 1)))
        g.add((prop_node, SH.qualifiedValueShape, qual_val_shape))
        return

    qual_val_shape = BNode()
    target_type = members[0]

    add_qual_val_shape = True

    fixed_value = cls._resolve_fixed_default(field_obj)
    has_fixed_value = not isinstance(fixed_value, _MISSING_TYPE)

    # Check if this is a literal type
    if has_fixed_value and isinstance(fixed_value, Literal):
        g.add((qual_val_shape, SH.hasValue, fixed_value))
    # Check if target is a Resource subclass
    elif hasattr(target_type, '_get_iri'):
        g.add((qual_val_shape, SH['class'], RdfExporter._class_iri_for_type(target_type)))
        RdfExporter._add_nested_pin_node(g, qual_val_shape, target_type)
    # For other types, use hasValue if a default is provided
    elif has_fixed_value and fixed_value is not None:
        g.add((qual_val_shape, SH.hasValue, fixed_value))
    else:
        add_qual_val_shape = False

    if add_qual_val_shape:
        label = field_obj.metadata.get('label', field_name)
        g.add((qual_val_shape, RDFS.label, Literal(label)))
        # Use the field's own declared min/max (defaulting min to 1, matching
        # required_field()'s default) instead of a hardcoded qualifiedMinCount
        # of 1 - that asserted "at least 1" even for fields explicitly
        # declared min=0 (e.g. ConnectionPoint.connection).
        qualified_min = field_obj.metadata.get('min')
        if qualified_min is None:
            qualified_min = 1
        g.add((prop_node, SH.qualifiedMinCount, Literal(qualified_min)))
        qualified_max = field_obj.metadata.get('max')
        if qualified_max is not None:
            g.add((prop_node, SH.qualifiedMaxCount, Literal(qualified_max)))
        g.add((prop_node, SH.qualifiedValueShape, qual_val_shape))
        g.add((qual_val_shape, RDF.type, SH.NodeShape))
