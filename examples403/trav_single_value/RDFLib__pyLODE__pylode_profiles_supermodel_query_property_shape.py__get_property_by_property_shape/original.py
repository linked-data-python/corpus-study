# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/property_shape.py
# region: get_property_by_property_shape (lines 69-73, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import RDF, SH, BNode, Dataset, Graph, Literal, URIRef
from pylode.profiles.supermodel.query import get_name

name = (
    kwargs.get("name")
    or profile_graph.value(property_shape, SH.name)
    or get_name(sh_path, profile_graph, db)
)
