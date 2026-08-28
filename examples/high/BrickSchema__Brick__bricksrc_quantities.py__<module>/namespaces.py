# Context shim (see meta.json): subset of bricksrc/namespaces.py from
# BrickSchema/Brick@c12949f236, so the region executes outside the package.
# Identical bindings for both representations.
from rdflib import Namespace

BRICK = Namespace("https://brickschema.org/schema/Brick#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

# QUDT namespaces
QUDT = Namespace("http://qudt.org/schema/qudt/")
QUDTQK = Namespace("http://qudt.org/vocab/quantitykind/")
QUDTDV = Namespace("http://qudt.org/vocab/dimensionvector/")
UNIT = Namespace("http://qudt.org/vocab/unit/")
