# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/synthesizer/synthesizer.py
# region: ConditionCache.register (lines 73-78, stratum bind_initbindings)
# licence of the source repository: see meta.json
def register(self, node, condition):
    if node not in self.node:
        self.node[node] = {}
    if condition not in self.node[node]:
        res = self.g.query(condition, initBindings={"node": node})
        self.node[node][condition] = res
