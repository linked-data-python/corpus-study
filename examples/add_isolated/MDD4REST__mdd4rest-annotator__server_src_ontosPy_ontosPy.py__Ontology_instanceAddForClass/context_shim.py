# Context shim (see meta.json): restores the liaison instanceAddForClass
# needs but the extracted lines (1168-1188) don't carry -- `self` is a
# method parameter, and its three attributes (self.allclasses,
# self.sessionGraph, self.sessionNS) are set up elsewhere in
# Ontology.__init__ / Ontology.setOntology, not in this region.
#
# OntologyContext reproduces only the shape those three attributes have in
# the real class (a plain list of class URIRefs, a fresh rdflib.Graph, a
# Namespace) -- without the ontology-file-parsing machinery around them,
# which the region never touches -- and DEFAULT_SESSION_NAMESPACE is the
# real constant, from MDD4REST/mdd4rest-annotator@c46839aa3d :
# server/src/ontosPy/ontosPy.py (lines 55, 90, 102-104, 140, 161-162).
# Identical bindings for both representations.
import rdflib
from rdflib import Namespace

DEFAULT_SESSION_NAMESPACE = "http://www.example.org/session/resource#"


class OntologyContext:
    """Minimal stand-in for Ontology: only what instanceAddForClass reads
    or writes through `self`."""

    def __init__(self, allclasses):
        self.allclasses = allclasses
        self.sessionGraph = rdflib.Graph()
        self.sessionNS = Namespace(DEFAULT_SESSION_NAMESPACE)
