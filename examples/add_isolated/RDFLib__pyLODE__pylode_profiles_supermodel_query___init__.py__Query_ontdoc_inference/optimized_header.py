# Extracted from RDFLib/pyLODE@0d0471fb99 : pylode/profiles/supermodel/query/__init__.py
# region: Query.ontdoc_inference (lines 614-622, stratum add_isolated)
# licence of the source repository: see meta.json
from context_shim import g
from rdflib.namespace import DC, DCTERMS, SDO

for s_, o in g.subject_objects(DC.creator | SDO.creator | SDO.author):
    g -= [(s_, p, o) for p in (DC.creator, SDO.creator, SDO.author)]
    g.add((s_, DCTERMS.creator, o))
