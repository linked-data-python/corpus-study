# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/synthesizer/graph_factories/spatial_relations.py
# region: SpatialRelationsCoordinates.compose_pose (lines 133-139, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import collection, BNode, Literal, RDF
from kindynsyn.namespaces import GEOM_ENT, GEOM_REL, GEOM_COORD, GEOM_OP, \
    QUDT_SCHEMA, QUDT_QKIND, QUDT_UNIT
from kindynsyn.rdflib_tools.helpers import uuid_ref

def compose_pose(self, in1, in2, composite):
    id_ = uuid_ref()
    self.g.add((id_, RDF["type"], GEOM_OP["ComposePose"]))
    self.g.add((id_, GEOM_OP["in1"], in1))
    self.g.add((id_, GEOM_OP["in2"], in2))
    self.g.add((id_, GEOM_OP["composite"], composite))
    return id_
