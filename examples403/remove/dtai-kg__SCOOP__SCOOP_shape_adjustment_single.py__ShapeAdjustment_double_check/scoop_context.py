# Context shim (see meta.json): subset of SCOOP/shape_adjustment_single.py from
# dtai-kg/SCOOP@40c6fc0420, so the region executes outside the class.
# double_check is a method: it reads three attributes of self, bound upstream by
# __init__ (shaclNS, adjusted_graph, adjusted_identifier) and filled by
# adjust() and reassign_identifier().  Identical bindings for both
# representations.
from rdflib import Graph, Namespace


class ShapeAdjustment:
    def __init__(self, adjusted_graph: Graph, adjusted_identifier: list):
        self.shaclNS = Namespace('http://www.w3.org/ns/shacl#')
        self.adjusted_graph = adjusted_graph
        self.adjusted_identifier = adjusted_identifier
