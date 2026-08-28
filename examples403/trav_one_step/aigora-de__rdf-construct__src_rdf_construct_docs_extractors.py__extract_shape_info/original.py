# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/docs/extractors.py
# region: extract_shape_info (lines 1021-1131, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import BNode, RDF, RDFS, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, SH, SKOS
FIRST_CLASS_SHACL_CONSTRAINTS = frozenset(
    [
        SH.path,
        SH.minCount,
        SH.maxCount,
        SH.datatype,
        SH["class"],  # 'class' is a Python keyword
        SH.nodeKind,
        SH["in"],  # 'in' is a Python keyword
        SH.hasValue,
        SH.pattern,
        SH.minLength,
        SH.maxLength,
        SH.minInclusive,
        SH.maxInclusive,
        SH.targetClass,
        SH.targetNode,
        SH.targetSubjectsOf,
        SH.targetObjectsOf,
        SH.closed,
        SH.ignoredProperties,
        SH.name,
        SH.description,
    ]
)

def extract_shape_info(graph: Graph, uri: URIRef) -> ShapeInfo:
    """Extract comprehensive information about a SHACL shape.

    Handles both NodeShapes and named PropertyShapes (distinguished
    via the ``kinds`` field). For NodeShapes, ``sh:property`` arcs
    are recursively extracted as :class:`PropertyShapeInfo` entries
    so renderers can inline them on the shape's page.

    Args:
        graph: RDF graph to query.
        uri: Shape URI to extract info for.

    Returns:
        ShapeInfo with all available metadata.
    """
    info = ShapeInfo(
        uri=uri,
        qname=get_qname(graph, uri),
        label=get_label(graph, uri),
        definition=get_definition(graph, uri),
        annotations=get_annotations(graph, uri),
        deprecated=_is_deprecated(graph, uri),
    )

    is_node_shape = (uri, RDF.type, SH.NodeShape) in graph
    is_property_shape = (uri, RDF.type, SH.PropertyShape) in graph

    info.kinds = [EntityKind.SHAPE]
    if is_node_shape:
        info.kinds.append(EntityKind.NODE_SHAPE)
    if is_property_shape:
        info.kinds.append(EntityKind.PROPERTY_SHAPE)
    # A shape can be declared an individual too — stage 1 routed such a
    # shape to shapes/ but recorded nothing about the declaration (#64).
    if _is_named_individual(graph, uri):
        info.kinds.append(EntityKind.NAMED_INDIVIDUAL)
    # If neither (shouldn't happen since the caller only passes shape URIs)
    # we still mark it as a shape so renderers don't crash on missing kind.

    # Top-level (NodeShape and PropertyShape both can have these)
    for obj in graph.objects(uri, SH.targetClass):
        if isinstance(obj, URIRef):
            info.target_classes.append(obj)
    for obj in graph.objects(uri, SH.targetNode):
        if isinstance(obj, URIRef):
            info.target_nodes.append(obj)
    for obj in graph.objects(uri, SH.targetSubjectsOf):
        if isinstance(obj, URIRef):
            info.target_subjects_of.append(obj)
    for obj in graph.objects(uri, SH.targetObjectsOf):
        if isinstance(obj, URIRef):
            info.target_objects_of.append(obj)

    # NodeShape structural fields
    if is_node_shape:
        for obj in graph.objects(uri, SH.closed):
            if isinstance(obj, Literal):
                info.closed = bool(obj)
                break
        ignored_head = next(iter(graph.objects(uri, SH.ignoredProperties)), None)
        if ignored_head is not None:
            members = _walk_rdf_list(graph, ignored_head)
            info.ignored_properties = [m for m in members if isinstance(m, URIRef)]

        # Property shape arcs — extract each as a PropertyShapeInfo
        for prop_node in graph.objects(uri, SH.property):
            # prop_node is typically a blank node; extract_property_shape_info
            # handles both blank and named cases.
            info.properties.append(extract_property_shape_info(graph, prop_node))

    # If this shape is itself a PropertyShape, capture its own constraints.
    if is_property_shape:
        info.property_shape = extract_property_shape_info(graph, uri)

    # Generic fallback for any non-first-class SHACL predicate at the
    # top level — same approach as PropertyShapeInfo.other_constraints.
    handled_at_top_level = {
        SH.targetClass,
        SH.targetNode,
        SH.targetSubjectsOf,
        SH.targetObjectsOf,
        SH.closed,
        SH.ignoredProperties,
        SH.property,
        # Also skip things already captured via get_label/get_definition/etc.
        RDFS.label,
        RDFS.comment,
        RDF.type,
    }
    for pred, obj in graph.predicate_objects(uri):
        if not isinstance(pred, URIRef):
            continue
        if pred in handled_at_top_level:
            continue
        # Only collect predicates in the SHACL namespace as "other constraints";
        # arbitrary annotations are already captured via get_annotations().
        if not str(pred).startswith(str(SH)):
            continue
        # Skip predicates we capture per-PropertyShape (they shouldn't
        # appear at the top level of a NodeShape, but PropertyShape-as-shape
        # captures them via info.property_shape above).
        if is_property_shape and pred in FIRST_CLASS_SHACL_CONSTRAINTS:
            continue
        if pred not in info.other_constraints:
            info.other_constraints[pred] = []
        if isinstance(obj, Literal):
            info.other_constraints[pred].append(str(obj))
        elif isinstance(obj, URIRef):
            info.other_constraints[pred].append(obj)

    return info
