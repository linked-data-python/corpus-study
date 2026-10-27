# Context shim (see meta.json): SparqlEngine reduced to what
# _new_fact_node reads off it as a bare global name (not through `self` --
# the region reads `SparqlEngine.PRED_FACT_H` etc. directly), from
# shijx12/KQAPro_Baselines@14d87cd22eb79f702fd4ad5c09240bef126d9dce,
# SPARQL/sparql_engine.py.


class SparqlEngine:
    """Minimal stand-in: _new_fact_node only reads these three class
    constants (used as keys into self.nodes, the real per-instance
    predicate registry -- see driver.py for how that is faked).
    As in the repository (SPARQL/sparql_engine.py:41-43) they are plain
    `str`, not URIRef: they are dictionary keys, and self.nodes maps them
    to URIRef(legal(p))."""

    PRED_FACT_H = 'pred:fact_h'     # link qualifier node to its head
    PRED_FACT_R = 'pred:fact_r'
    PRED_FACT_T = 'pred:fact_t'
