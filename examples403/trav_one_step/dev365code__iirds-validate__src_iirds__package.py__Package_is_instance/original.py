# Extracted from dev365code/iirds-validate@4b3f840df8 : src/iirds/_package.py
# region: Package.is_instance (lines 277-279, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS

def is_instance(self, node, cls) -> bool:
    return bool(set(self.graph.objects(node, RDF.type))
                & subclasses_of(self.graph, cls))
