# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_adjustment_single.py
# region: ShapeAdjustment.findNode (lines 418-425, stratum remove)
# licence of the source repository: see meta.json
def findNode(self, node):
    for o in self.initial_graph.objects(node, self.shaclNS.node):
        self.adjusted_shape.append(o)
        for target in ("targetClass", "targetNode", "targetObjectsOf", "targetSubjectsOf"):
            self.initial_graph.remove((o, self.shaclNS[target], None))
        self.findNode(o)
