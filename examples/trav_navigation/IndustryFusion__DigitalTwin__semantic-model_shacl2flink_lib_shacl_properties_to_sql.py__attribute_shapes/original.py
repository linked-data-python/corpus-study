# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/shacl2flink/lib/shacl_properties_to_sql.py
# region: attribute_shapes (lines 1757-1781, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF, BNode
from rdflib.namespace import SH
NGSILD_VALUE_PATHS = frozenset(VALUE_PATH_ATTRIBUTE_TYPES)

def attribute_shapes(g):
    """
    Every property shape that names an NGSI-LD attribute, with its node shape.

    These are the shapes that must produce constraints. Only node-level
    connectives are descended through: a shape nested inside an attribute shape
    describes that attribute -- its value (ngsi-ld:hasValue and friends), or its
    rdf:type -- rather than naming an attribute of its own, and the compiler
    folds those into the attribute's constraint instead of emitting one.
    """
    for nodeshape in g.subjects(RDF.type, SH.NodeShape):
        if not list(g.objects(nodeshape, SH.targetClass)):
            continue
        seen, frontier = set(), [nodeshape]
        while frontier:
            shape = frontier.pop()
            if shape in seen:
                continue
            seen.add(shape)
            frontier.extend(connective_clauses(g, shape))
            for prop in g.objects(shape, SH.property):
                paths = list(g.objects(prop, SH.path))
                if len(paths) == 1 and str(paths[0]) not in NGSILD_VALUE_PATHS \
                        and paths[0] != RDF.type:
                    yield nodeshape, prop, paths[0]
