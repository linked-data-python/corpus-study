# Extracted from shijx12/KQAPro_Baselines@14d87cd22e : SPARQL/sparql_engine.py
# region: SparqlEngine._new_fact_node (lines 129-134, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Literal, XSD
from context_shim import SparqlEngine

def _new_fact_node(self, h, r, t):
    node = BNode()
    self.graph.add((node, self.nodes[SparqlEngine.PRED_FACT_H], h))
    self.graph.add((node, self.nodes[SparqlEngine.PRED_FACT_R], r))
    self.graph.add((node, self.nodes[SparqlEngine.PRED_FACT_T], t))
    return node
