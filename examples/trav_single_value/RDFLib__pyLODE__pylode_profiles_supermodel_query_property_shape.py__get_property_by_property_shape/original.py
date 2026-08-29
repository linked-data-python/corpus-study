# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/property_shape.py
# region: get_property_by_property_shape (lines 69-73, stratum trav_single_value)
# licence of the source repository: see meta.json
#
# The region is a bare statement inside get_property_by_property_shape, not a
# function of its own: kwargs, profile_graph, property_shape, sh_path and db
# are parameters of the enclosing (much larger) function. They are restored
# here as parameters of a small wrapper -- "un paramètre annoté" per
# AGENT_BATCH.md -- which also makes `name` observable to the driver: the
# statement produces no graph and prints nothing, so run_pair's module-state
# comparison has nothing to compare it against; entry="compute_name" does.
# get_name is the project's own helper (pylode.profiles.supermodel.query);
# pylode is not installed here, so it comes from the context shim instead
# (see meta.json).
from rdflib import RDF, SH, BNode, Dataset, Graph, Literal, URIRef
from pylode_context import get_name


def compute_name(kwargs, profile_graph, property_shape, sh_path, db):
    name = (
        kwargs.get("name")
        or profile_graph.value(property_shape, SH.name)
        or get_name(sh_path, profile_graph, db)
    )
    return name
