# Extracted from linkml/linkml@680595df54 : tests/linkml/test_generators/test_shaclgen.py
# region: _get_prop_objects (lines 1427-1433, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import RDF, RDFS, SH, Literal, URIRef

def _get_prop_objects(g, shape_uri, prop_path_uri, predicate):
    """Get predicate values for the property shape with the given sh:path."""
    for prop_node in g.objects(shape_uri, SH.property):
        paths = list(g.objects(prop_node, SH.path))
        if paths and paths[0] == prop_path_uri:
            return list(g.objects(prop_node, predicate))
    return []
