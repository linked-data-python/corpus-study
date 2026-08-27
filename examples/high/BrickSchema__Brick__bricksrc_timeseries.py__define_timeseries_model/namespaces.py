# Context shim (see meta.json): subset of bricksrc/namespaces.py from
# BrickSchema/Brick@c12949f236, so the region executes outside the package.
# Identical bindings for both representations.
from rdflib import Namespace

BRICK = Namespace("https://brickschema.org/schema/Brick#")
SH = Namespace("http://www.w3.org/ns/shacl#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
A = RDF.type
