# Extracted from jupyrdf/ipyradiant@2cff79e054 : src/ipyradiant/query/framer.py
# region: SPARQLQueryFramer.print_vars (lines 89-100, stratum bind_initbindings)
# licence of the source repository: see meta.json
import logging
from rdflib import Graph, URIRef
from rdflib.plugins.sparql import prepareQuery

@classmethod
def print_vars(cls) -> None:
    """Utility function to print variables that may be used as bindings"""
    logging.info("Only variables in the SELECT line are printed.")
    tmp_graph = Graph()
    # Run fake query to print vars
    if not cls.query:
        tmp_query = prepareQuery(cls.sparql, initNs=cls.initNs)
        tmp_res = tmp_graph.query(tmp_query)
    else:
        tmp_res = tmp_graph.query(cls.query)
    print("Vars:\n", sorted([str(var) for var in tmp_res.vars]))
