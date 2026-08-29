# Context shim (see meta.json): stand-ins for names generate_brick.py relies
# on but that fall outside this region's extraction, from
# BrickSchema/Brick@c12949f236 (generate_brick.py):
#
#   - BRICK, BSH, REC, RDF, OWL, RDFS, TAG, SOSA, SKOS, QUDT, VCARD, SH, REF
#     are the real IRIs, copied verbatim (the subset this region imports)
#     from bricksrc/namespaces.py -- that package is not installed and pulls
#     in the rest of the Brick build toolchain.
#   - `Graph`, reached as `brickschema.Graph()` (generate_brick.py line 4:
#     `import brickschema`; line 73: `G = brickschema.Graph()`), stands in
#     for the real brickschema.Graph: a heavyweight rdflib.Graph subclass
#     that loads and imports ontology files through ontoenv on construction
#     (not installed; network access at import time is undesirable for a
#     test fixture anyway). define_relationships only ever reaches it as
#     the *default* value of its `graph=` parameter -- every call in this
#     pair's driver passes an explicit `graph=`, so a plain rdflib.Graph is
#     enough for `G = brickschema.Graph()` (module level) not to raise.
#   - `add_relationships` (generate_brick.py lines 85-91) is a sibling
#     top-level function that define_relationships calls at its own end,
#     for the propdefn keys it does not itself handle. Reproduced verbatim.
#
# Identical bindings for both representations.
from rdflib import Namespace, Graph

BRICK = Namespace("https://brickschema.org/schema/Brick#")
TAG = Namespace("https://brickschema.org/schema/BrickTag#")
BSH = Namespace("https://brickschema.org/schema/BrickShape#")
REF = Namespace("https://brickschema.org/schema/Brick/ref#")
SH = Namespace("http://www.w3.org/ns/shacl#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
REC = Namespace("https://w3id.org/rec#")
QUDT = Namespace("http://qudt.org/schema/qudt/")


def add_relationships(item, propdefs, graph=None):
    for propname, propval in propdefs.items():
        if isinstance(propval, list):
            for pv in propval:
                graph.add((item, propname, pv))
        elif not isinstance(propval, dict):
            graph.add((item, propname, propval))
