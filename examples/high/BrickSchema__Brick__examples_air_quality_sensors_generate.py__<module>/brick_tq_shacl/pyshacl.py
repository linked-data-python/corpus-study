# Context shim (see meta.json): stand-in for brick_tq_shacl.pyshacl.
#
# The real `infer` runs the topquadrant SHACL engine (a Java process) over the
# model plus the full Brick ontology.  Neither the engine nor Brick.ttl is
# available here, so `infer` returns the graph unchanged -- identically on
# both sides, so the comparison stays a comparison of the two representations.


def infer(graph, *args, **kwargs):
    """No-op stand-in for brick_tq_shacl.pyshacl.infer."""
    return graph
