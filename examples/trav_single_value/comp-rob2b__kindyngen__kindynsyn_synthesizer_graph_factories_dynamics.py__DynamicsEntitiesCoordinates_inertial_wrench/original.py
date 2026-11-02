# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/synthesizer/graph_factories/dynamics.py
# region: DynamicsEntitiesCoordinates.inertial_wrench (lines 202-222, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import collection, BNode, Literal, RDF
from kindynsyn.namespaces import GEOM_ENT, GEOM_REL, GEOM_COORD, RBDYN_ENT, \
    RBDYN_COORD, RBDYN_OP, QUDT_SCHEMA, QUDT_QKIND, QUDT_UNIT
from kindynsyn.rdflib_tools.helpers import uuid_ref

def inertial_wrench(self, rigid_body_inertia, velocity_twist, wrench):
    assert self.g.value(rigid_body_inertia, RBDYN_COORD["as-seen-by"]) == self.g.value(velocity_twist, GEOM_COORD["as-seen-by"])
    assert self.g.value(rigid_body_inertia, RBDYN_COORD["as-seen-by"]) == self.g.value(wrench, RBDYN_COORD["as-seen-by"])
    assert self.g.value(rigid_body_inertia, RBDYN_COORD["of-inertia"] / RBDYN_ENT["about"]) == self.g.value(velocity_twist, GEOM_COORD["of-velocity"] / GEOM_REL["reference-point"])
    assert self.g.value(rigid_body_inertia, RBDYN_COORD["of-inertia"] / RBDYN_ENT["about"]) == self.g.value(wrench, RBDYN_COORD["of-wrench"] / RBDYN_ENT["reference-point"])
    assert self.g.value(rigid_body_inertia, RBDYN_COORD["of-inertia"] / RBDYN_ENT["of-body"]) == self.g.value(velocity_twist, GEOM_COORD["of-velocity"] / GEOM_REL["of"])
    assert self.g.value(rigid_body_inertia, RBDYN_COORD["of-inertia"] / RBDYN_ENT["of-body"]) == self.g.value(wrench, RBDYN_COORD["of-wrench"] / RBDYN_ENT["acts-on"])
    assert QUDT_UNIT["KiloGM"] in self.g[rigid_body_inertia : QUDT_SCHEMA["unit"]]
    assert QUDT_UNIT["M-KiloGM"] in self.g[rigid_body_inertia : QUDT_SCHEMA["unit"]]
    assert QUDT_UNIT["KiloGM-M2"] in self.g[rigid_body_inertia : QUDT_SCHEMA["unit"]]
    assert QUDT_UNIT["RAD-PER-SEC"] in self.g[velocity_twist : QUDT_SCHEMA["unit"]]
    assert QUDT_UNIT["M-PER-SEC"] in self.g[velocity_twist : QUDT_SCHEMA["unit"]]
    assert QUDT_UNIT["N-M"] in self.g[wrench : QUDT_SCHEMA["unit"]]
    assert QUDT_UNIT["N"] in self.g[wrench : QUDT_SCHEMA["unit"]]

    id_ = uuid_ref()
    self.g.add((id_, RDF["type"], RBDYN_OP["InertialWrench"]))
    self.g.add((id_, RBDYN_OP["rigid-body-inertia"], rigid_body_inertia))
    self.g.add((id_, RBDYN_OP["velocity-twist"], velocity_twist))
    self.g.add((id_, RBDYN_OP["wrench"], wrench))
    return id_
