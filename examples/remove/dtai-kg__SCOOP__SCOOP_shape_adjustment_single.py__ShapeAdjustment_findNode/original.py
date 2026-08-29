# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_adjustment_single.py
# region: ShapeAdjustment.findNode (lines 418-425, stratum remove)
# licence of the source repository: see meta.json
def findNode(self, node):
    for s, p, o in self.initial_graph.triples((node, self.shaclNS.node, None)):
        self.adjusted_shape.append(o)
        self.initial_graph.remove((o, self.shaclNS.targetClass, None))
        self.initial_graph.remove((o, self.shaclNS.targetNode, None))
        self.initial_graph.remove((o, self.shaclNS.targetObjectsOf, None))
        self.initial_graph.remove((o, self.shaclNS.targetSubjectsOf, None))
        self.findNode(o)
