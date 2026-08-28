# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: get_root_profile_iri (lines 293-312, band high)
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

def get_root_profile_iri(graph: Graph) -> URIRef:
    """Get the root profile IRI in the initial document.

    This also ensures there is only 1 profile in the initial document.
    """
    profiles = list(graph.subjects(RDF.type, PROF.Profile, unique=True))
    count = len(profiles)
    if count > 1:
        raise ValueError(
            f"There is more than 1 prof:Profile defined in the input document. Expected only 1 prof:Profile definition but found {[str(p) for p in profiles]}."
        )
    elif count < 1:
        profiles = list(graph.subjects(RDF.type, OWL.Ontology, unique=True))

        if len(profiles) != 1:
            raise ValueError(
                f"There can only be one owl:Ontology defined in the document."
            )

    return profiles[0]
