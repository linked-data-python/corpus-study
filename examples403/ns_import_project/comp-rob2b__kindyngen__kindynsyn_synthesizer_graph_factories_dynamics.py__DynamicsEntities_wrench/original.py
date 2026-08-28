# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/synthesizer/graph_factories/dynamics.py
# region: DynamicsEntities.wrench (lines 12-19, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import collection, BNode, Literal, RDF
from kindynsyn.namespaces import GEOM_ENT, GEOM_REL, GEOM_COORD, RBDYN_ENT, \
    RBDYN_COORD, RBDYN_OP, QUDT_SCHEMA, QUDT_QKIND, QUDT_UNIT
from kindynsyn.rdflib_tools.helpers import uuid_ref

def wrench(self, acts_on, reference_point):
    id_ = uuid_ref()
    self.g.add((id_, RDF["type"], RBDYN_ENT["Wrench"]))
    self.g.add((id_, RBDYN_ENT["acts-on"], acts_on))
    self.g.add((id_, RBDYN_ENT["reference-point"], reference_point))
    self.g.add((id_, QUDT_SCHEMA["quantityKind"], QUDT_QKIND["Torque"]))
    self.g.add((id_, QUDT_SCHEMA["quantityKind"], QUDT_QKIND["Force"]))
    return id_
