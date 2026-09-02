# Context shim (see meta.json): the region's `__init__` was extracted from
# inside class MaxLengthConstraintComponent, so `super(MaxLengthConstraintComponent,
# self).__init__(shape)` needs the real class name AND an already-constructed
# `self` whose MRO matches it -- the extracted body alone never names its own
# class hierarchy. Minimal stand-ins for RDFLib/pySHACL@469cca7a22, reproducing
# only what this __init__ touches:
#
#   pyshacl/shape.py:202-203        Shape.objects(predicate) ==
#                                    self.sg.graph.objects(self.node, predicate)
#   pyshacl/constraints/constraint_component.py:61  ConstraintComponent.__init__
#                                    sets self.shape = shape, nothing else
#   pyshacl/constraints/core/string_based_constraints.py:43-46
#                                    StringBasedConstraintBase.__init__ calls
#                                    super().__init__(shape), then sets
#                                    self.string_rules = [], self.allow_multi_rules = True
#                                    (both are immediately overwritten by the
#                                    region itself, so the exact starting
#                                    values do not matter to this test)
#
# Identical shim for both representations.
from rdflib import Graph, URIRef


class Shape:
    def __init__(self, graph: Graph, node: URIRef):
        self.graph = graph
        self.node = node

    def objects(self, predicate=None):
        return self.graph.objects(self.node, predicate)


class ConstraintComponent:
    def __init__(self, shape):
        self.shape = shape


class StringBasedConstraintBase(ConstraintComponent):
    def __init__(self, shape):
        super().__init__(shape)
        self.string_rules = []
        self.allow_multi_rules = True


class MaxLengthConstraintComponent(StringBasedConstraintBase):
    pass
