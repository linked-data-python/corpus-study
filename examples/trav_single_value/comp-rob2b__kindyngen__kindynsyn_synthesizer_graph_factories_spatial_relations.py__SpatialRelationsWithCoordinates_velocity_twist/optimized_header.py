# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/synthesizer/graph_factories/spatial_relations.py
# region: SpatialRelationsWithCoordinates.velocity_twist (lines 204-210, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import RDF
from kindynsyn.namespaces import GEOM_ENT

def velocity_twist(self, of, with_respect_to, as_seen_by, reference_point=None, angular_velocity=None, linear_velocity=None):
    assert GEOM_ENT.Frame in self.rel.g[as_seen_by : RDF.type]
    reference_point = reference_point or self.rel.g.value(as_seen_by, GEOM_ENT.origin)
    return self.coord.velocity_twist(
        self.rel.velocity(of, with_respect_to, reference_point),
        as_seen_by, angular_velocity, linear_velocity
    )
