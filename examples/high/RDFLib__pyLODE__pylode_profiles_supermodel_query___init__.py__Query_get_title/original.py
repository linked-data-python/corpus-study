# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_title (lines 505-507, band high)
# licence of the source repository: see meta.json
from rdflib.namespace import (
    DC,
    DCTERMS,
    FOAF,
    ORG,
    OWL,
    PROF,
    PROV,
    QB,
    RDF,
    RDFS,
    SDO,
    SH,
    SKOS,
    VANN,
)

def get_title(self, iri: str) -> str | None:
    for o2 in self.graph.objects(iri, DCTERMS.title):
        return str(o2)
