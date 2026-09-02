# Context shim (see meta.json): subset of the same source file's own
# module-level helpers -- initial_kg, build_aq_iris, build_aqsys_iris (all
# defined earlier in datasets/groundwater/il-isgs/IL_ISGS_Aquifer-AqSystem-2ttl.py
# at SAWGraph/water-kg@032ec41357, lines 243-275, copied verbatim) -- plus a
# _PREFIX dict and a find_s2_intersects_poly stub standing in for the
# project's namespaces.py (not part of this repository, referenced by
# `sys.path.insert` against a sibling checkout), so the region executes
# outside the package. Identical bindings for both representations.
from rdflib import Namespace

max_id_length = 4

_PREFIX = {
    "gwml2": Namespace("http://www.opengis.net/ont/gwml-main/2.0#"),
    "il_isgs": Namespace("https://gsis.isgs.illinois.edu/def/"),
    "il_isgs_data": Namespace("https://gsis.isgs.illinois.edu/data/"),
    "saw_water": Namespace("https://cka.sawgraph.link/water#"),
    "sf": Namespace("http://www.opengis.net/ont/sf#"),
}


def find_s2_intersects_poly(*args, **kwargs):
    """Not called by process_aquifers_shp2ttl; present only so the import succeeds."""
    raise NotImplementedError


def initial_kg(_PREFIX):
    """Create an empty knowledge graph with project namespaces (verbatim, see header)."""
    from rdflib import Graph
    graph = Graph()
    for prefix in _PREFIX:
        graph.bind(prefix, _PREFIX[prefix])
    return graph


def build_aq_iris(aqid, _PREFIX):
    """Create IRIs for an aquifer and its geometry (verbatim, see header)."""
    return (_PREFIX["il_isgs_data"]['d.ISGS-Aquifer.' + aqid],
            _PREFIX["il_isgs_data"]['d.ISGS-Aquifer.Geometry.' + aqid])


def build_aqsys_iris(aqsysid, _PREFIX):
    """Create IRIs for an aquifer system and its geometry (verbatim, see header)."""
    return (_PREFIX["il_isgs_data"]['d.SAW-Aquifer-System.CM' + str(aqsysid).zfill(max_id_length)],
            _PREFIX["il_isgs_data"]['d.SAW-Aquifer-System.Geometry.CM' + str(aqsysid).zfill(max_id_length)])
