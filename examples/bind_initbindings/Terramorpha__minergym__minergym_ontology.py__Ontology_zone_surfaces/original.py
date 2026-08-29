# Extracted from Terramorpha/minergym@1d2d586bb1 : minergym/ontology.py
# region: Ontology.zone_surfaces (lines 126-135, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.term import Node

def zone_surfaces(self, zone: Node) -> list[Node]:
    """Return all the surfaces that have `zone_name` equal to `zone`."""

    q = """# -*- mode: sparql -*-
SELECT ?surface
WHERE {
  ?surface a "BuildingSurface:Detailed" .
  ?surface idf:zone_name ?zone .
}"""
    return [r.surface for r in self.rdf.query(q, initBindings={"zone": zone})]
