# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/synthesizer/synthesizer.py
# region: TreeExpander.expand (lines 135-152, stratum bind_initbindings)
# licence of the source repository: see meta.json
import rdflib

def expand(self, node: rdflib.URIRef) -> dict[rdflib.URIRef, dict[str, list[CompiledExpander]]]:
    # Try applying any expander query and if it returns neighbour nodes
    # attach them to the final result list together with the dispatcher
    # functions.
    ret = {}
    for query, expander in self.expanders.items():
        res = self.graph.query(query, initBindings={"node": node})
        for row in res:
            child = row["child"]

            # There can be multiple queries leading to the _same_ child, so
            # the associated expanders/traversers are collected in a list
            if child not in ret:
                ret[child] = {}
            if query not in ret[child]:
                ret[child][query] = []
            ret[child][query].append(expander)
    return ret
