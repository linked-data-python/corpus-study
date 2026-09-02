# Context shim (see meta.json): stand-in for the `Entity` receiver
# `add_contentclass_if_missing` needs as `self`, from
# semantic-model/opcua/lib/entity.py in IndustryFusion/DigitalTwin@3b40088b88.
# The real class builds `self.e` (its own knowledge graph, a plain
# rdflib.Graph -- confirmed at line 73 of the source: `self.e = Graph()`) in
# a many-line `__init__` this region never calls, and `add_enum_class` is a
# real method with its own graph-building logic the region under test
# never runs -- it only calls it, or doesn't. So the stand-in keeps exactly
# that shape: `self.e` as a plain Graph a test can pre-populate, and
# `add_enum_class` recording that it was called (with what) rather than
# reproducing its body -- the same status as OntologyLinter's stand-in
# helpers in the trav_navigation sibling of this pattern.
from rdflib import Graph


class Entity:
    def __init__(self, e: Graph):
        self.e = e
        self.add_enum_class_calls = []

    def add_enum_class(self, graph, contentclass):
        self.add_enum_class_calls.append((graph, contentclass))
