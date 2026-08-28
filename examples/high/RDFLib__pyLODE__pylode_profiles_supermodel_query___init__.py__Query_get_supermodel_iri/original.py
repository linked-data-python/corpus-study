# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.get_supermodel_iri (lines 495-503, band high)
# licence of the source repository: see meta.json
from rdflib import Dataset, Graph, Literal, URIRef
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

def get_supermodel_iri(self) -> URIRef:
    iri = None
    for s in self.graph.subjects(RDF.type, PROF.Profile, unique=True):
        iri = s

    if iri is None:
        iri = self.root_profile_iri

    return iri
