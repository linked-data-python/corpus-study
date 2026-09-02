# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/entity.py
# region: Entity.add_contentclass_if_missing (lines 225-227, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, RDF, RDFS
from context_shim import Entity  # context shim -- see meta.json

def add_contentclass_if_missing(self, g, contentclass):
    if g.value(contentclass, RDF.type) is not None and self.e.value(contentclass, RDF.type) is None:
        self.add_enum_class(g, contentclass)


# Demo harness (identical on both sides, see meta.json): the region is a
# method whose only observable effects are calls to `self.add_enum_class`
# (its own body is a stand-in, see context_shim.py). `demo` builds a fresh
# `Entity` around `e_data` (the target's own knowledge graph, `self.e`),
# runs the region against `g` and `contentclass`, and returns whether
# `add_enum_class` was called -- the one bit of information the two
# `bool`-shaped existence reads (`g.value(...) is not None`,
# `self.e.value(...) is None`) actually decide.
def demo(g, e_data, contentclass):
    entity = Entity(e_data)
    add_contentclass_if_missing(entity, g, contentclass)
    return len(entity.add_enum_class_calls)
