# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/property_shape.py
# region: get_sh_path (lines 26-41, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import RDF, SH, BNode, Dataset, Graph, Literal, URIRef
from rdflib.collection import Collection

def get_sh_path(
    property_shape: URIRef | BNode, profile_graph: Graph, db: Dataset
) -> tuple[URIRef | None, Collection | None]:
    """Get the sh:path value of a property shape."""
    sh_path = db.value(property_shape, SH.path)

    if sh_path is None:
        return None, None
    elif isinstance(sh_path, BNode):
        rdf_list = Collection(db, sh_path)
        if rdf_list:
            # If it's a rdf:List with elements, assign the first element as the sh:path value.
            sh_path = rdf_list[0]
            return sh_path, rdf_list

    return sh_path, None
