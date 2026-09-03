# Extracted from jupyrdf/ipyradiant@2cff79e054 : src/ipyradiant/query/framer.py
# region: SPARQLQueryFramer.print_vars (lines 89-100, stratum bind_initbindings)
# licence of the source repository: see meta.json
# (added to make the region executable: `print_vars` is a classmethod that
# reads cls.query/cls.sparql/cls.initNs -- class attributes declared on
# SPARQLQueryFramer OUTSIDE the extracted lines. Restored verbatim from the
# real class body at this commit: initNs = {}, sparql = "", query = None,
# the three attributes this method actually reads; see meta.json.)
import logging
from rdflib import Graph, Namespace, URIRef
from rdflib.plugins.sparql import prepareQuery


class SPARQLQueryFramer:
    initNs = {}
    sparql = ""
    query = None

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


# Demo harness (identical on both sides, see meta.json): `print_vars` is a
# classmethod reading class attributes, not a function with arguments to
# vary, and it prints rather than returning a value -- entry=/calls= on
# `print_vars` itself would exercise only the class's default (empty) state
# every time. `demo` configures two subclasses that cover both of
# print_vars's branches (an unset `query`, falling through to
# `prepareQuery(cls.sparql, initNs=cls.initNs)`; an already-prepared
# `query`) and calls `.print_vars()` on each -- run_pair's per-call stdout
# capture is what actually gets compared.
def demo():
    class WithSparql(SPARQLQueryFramer):
        initNs = {"ex": Namespace("http://example.org/")}
        sparql = "SELECT ?s ?p WHERE { ?s ex:knows ?p }"

    class WithQuery(SPARQLQueryFramer):
        query = prepareQuery("SELECT ?a ?c WHERE { ?a a ?c }")

    WithSparql.print_vars()
    WithQuery.print_vars()
