# Context shim (see meta.json): subset of interior-night/kglab-ggg@735ae3c49c's
# kglab/gpviz.py, so the region (GPViz.__init__) executes outside the
# package. `_find_triples` walks the parsed SPARQL algebra to collect the
# triple patterns GPViz will later render; it is not part of the extracted
# region (the region only calls it once, at the end of __init__), so it is
# kept out of original.py/translated.ldpy to keep the surface-metrics
# comparison honest. Identical for both representations.
class GPVizBase:
    def _find_triples(self, algebra):
        return []


def summarize(cls, sparql, namespaces):
    """Build a `cls` instance and return its state as a plain, comparable
    dict -- driver.py's harness compares module-level values and function
    return values generically, and a bare `GPViz` instance has no `__eq__`,
    so comparing two instances directly always reports a spurious diff.
    Identical for both representations; not part of the extracted region.
    """
    obj = cls(sparql, namespaces)
    return {
        "namespaces": dict(obj.namespaces),
        "blank_nodes": list(obj.blank_nodes),
        "values": dict(obj.values),
        "triples": list(obj.triples),
    }
