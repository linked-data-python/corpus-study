# Context shim (see meta.json): subset of bricksrc/namespaces.py from
# BrickSchema/Brick@c12949f236, plus a minimal stand-in for the `brickschema`
# package (unused at call time -- it only backs the function's default
# `graph=` argument, which every call in driver.py overrides explicitly).
# Identical bindings for both representations.
from rdflib import Namespace
from rdflib.namespace import RDF, OWL, RDFS, SKOS

BRICK = Namespace("https://brickschema.org/schema/Brick#")
BSH = Namespace("https://brickschema.org/schema/BrickShape#")
REC = Namespace("https://w3id.org/rec#")
TAG = Namespace("https://brickschema.org/schema/BrickTag#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
QUDT = Namespace("http://qudt.org/schema/qudt/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
SH = Namespace("http://www.w3.org/ns/shacl#")
REF = Namespace("https://brickschema.org/schema/Brick/ref#")


class _BrickschemaStandIn:
    """Stand-in for the `brickschema` package: only `Graph` is used here,
    as the default value of `define_classes`'s `graph=` parameter."""
    from rdflib import Graph


brickschema = _BrickschemaStandIn()


def add_tags(classname, taglist, graph=None):
    """Stand-in for generate_brick.add_tags: outside the region, not
    exercised by driver.py's fixtures (empty tag lists), kept a no-op so
    both sides bind the same no-op."""
    pass


def define_constraints(constraints, classname, graph=None):
    """Stand-in for generate_brick.define_constraints: outside the region,
    not exercised by driver.py's fixtures (empty constraints), kept a
    no-op so both sides bind the same no-op."""
    pass
