# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/entity.py
# region: Entity.add_contentclass_if_missing (lines 225-227, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, RDF, RDFS

def add_contentclass_if_missing(self, g, contentclass):
    if g.value(contentclass, RDF.type) is not None and self.e.value(contentclass, RDF.type) is None:
        self.add_enum_class(g, contentclass)
