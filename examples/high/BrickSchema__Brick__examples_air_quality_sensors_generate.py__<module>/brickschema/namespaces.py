# Context shim (see meta.json): subset of brickschema/namespaces.py from the
# BrickSchema/py-brickschema checkout, so the region executes without the
# brickschema distribution.  Identical bindings for both representations.
from rdflib import Namespace

BRICK = Namespace("https://brickschema.org/schema/Brick#")
TAG = Namespace("https://brickschema.org/schema/BrickTag#")
BSH = Namespace("https://brickschema.org/schema/BrickShape#")
REF = Namespace("https://brickschema.org/schema/Brick/ref#")
BACNET = Namespace("http://data.ashrae.org/bacnet/2020#")

OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SH = Namespace("http://www.w3.org/ns/shacl#")
REC = Namespace("https://w3id.org/rec#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

QUDT = Namespace("http://qudt.org/schema/qudt/")
QUDTQK = Namespace("http://qudt.org/vocab/quantitykind/")
QUDTDV = Namespace("http://qudt.org/vocab/dimensionvector/")
UNIT = Namespace("http://qudt.org/vocab/unit/")

A = RDF.type


def bind_prefixes(graph, brick_version="1.3"):
    """Associate common prefixes with the graph (as py-brickschema does)."""
    graph.bind("rdf", RDF)
    graph.bind("owl", OWL)
    graph.bind("rdfs", RDFS)
    graph.bind("skos", SKOS)
    graph.bind("sh", SH)
    graph.bind("qudtqk", QUDTQK)
    graph.bind("qudt", QUDT)
    graph.bind("unit", UNIT)
    graph.bind("ref", REF)
    graph.bind("bacnet", BACNET)
    graph.bind("rec", REC)
    graph.bind("brick", BRICK)
    graph.bind("tag", TAG)
    graph.bind("bsh", BSH)
    graph.bind("xsd", XSD)
