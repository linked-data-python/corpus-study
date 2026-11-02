# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.ontdoc_inference (lines 614-622, stratum add_isolated)
# licence of the source repository: see meta.json
from itertools import chain
from context_shim import g
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

for s_, o in chain(
    g.subject_objects(DC.creator),
    g.subject_objects(SDO.creator),
    g.subject_objects(SDO.author),
):
    g.remove((s_, DC.creator, o))
    g.remove((s_, SDO.creator, o))
    g.remove((s_, SDO.author, o))
    g.add((s_, DCTERMS.creator, o))
