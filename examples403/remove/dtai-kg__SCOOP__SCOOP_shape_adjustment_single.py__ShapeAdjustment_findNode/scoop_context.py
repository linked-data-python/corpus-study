# Context shim (see meta.json): subset of SCOOP/shape_adjustment_single.py from
# dtai-kg/SCOOP@40c6fc0420, so the region executes outside the class.
# findNode is a method: it reads three attributes of self, bound upstream by
# __init__ (shaclNS), by adjust()/parseRawDataSchemaShape() (initial_graph) and
# by parseRML() (adjusted_shape).  Identical bindings for both representations.
from rdflib import Graph, Namespace


class ShapeAdjustment:
    def __init__(self, initial_graph: Graph):
        self.shaclNS = Namespace('http://www.w3.org/ns/shacl#')
        self.initial_graph = initial_graph
        self.adjusted_shape = []
