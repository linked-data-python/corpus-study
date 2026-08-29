# Context shim (see meta.json): SparqlEngine reduced to what
# _new_fact_node reads off it as a bare global name (not through `self` --
# the region reads `SparqlEngine.PRED_FACT_H` etc. directly), from
# shijx12/KQAPro_Baselines@14d87cd22eb79f702fd4ad5c09240bef126d9dce,
# SPARQL/sparql_engine.py.
from rdflib import URIRef


class SparqlEngine:
    """Minimal stand-in: _new_fact_node only reads these three class
    constants (used as keys into self.nodes, the real per-instance
    predicate registry -- see driver.py for how that is faked)."""

    PRED_FACT_H = URIRef("http://example.org/kqapro#fact_h")
    PRED_FACT_R = URIRef("http://example.org/kqapro#fact_r")
    PRED_FACT_T = URIRef("http://example.org/kqapro#fact_t")
