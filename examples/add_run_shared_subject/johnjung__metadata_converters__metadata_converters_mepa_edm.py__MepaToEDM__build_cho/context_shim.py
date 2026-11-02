# Context shim (see meta.json): the part of MepaToEDM
# (johnjung/metadata_converters@36a81d6a97, metadata_converters/mepa_edm.py)
# that line 201 of _build_cho reads, so the statement executes outside the
# class. Identical bindings for both representations.
#
# In the repository `self.graph` is the instance's rdflib Graph and
# `work_cho` / `recto_cho` are the URIRefs of the work and of its recto
# aggregated object, minted earlier in _build_cho.
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS

EX = Namespace("http://example.org/mepa/")


class MepaToEDM:
    def __init__(self):
        self.graph = Graph()
        # triples that are already there, one of them with the same subject
        # and the same predicate: they must survive
        self.work_cho = EX["work/1"]
        self.recto_cho = EX["work/1/recto"]
        self.graph.add((self.work_cho, DCTERMS.title, Literal("Work 1")))
        self.graph.add((self.work_cho, DCTERMS.hasPart, EX["work/1/verso"]))
        self.graph.add((self.recto_cho, DCTERMS.title, Literal("Recto of work 1")))


self = MepaToEDM()
graph = self.graph   # the graph the region writes to, exposed for the driver
