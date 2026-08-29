# Extracted from jupyrdf/ipyradiant@2cff79e054 : src/ipyradiant/query/framer.py
# region: SPARQLQueryFramer.run_query (lines 116-181, stratum bind_initbindings)
# licence of the source repository: see meta.json
import logging
from pandas import DataFrame
from rdflib import Graph, URIRef
from rdflib.plugins.sparql import prepareQuery

@classmethod
def run_query(
    cls,
    graph: Graph,
    initBindings: dict = None,
    initNs: dict = None,
    **initBindingsKwarg,
) -> DataFrame:
    """Runs a query with optional initBindings, and returns the results as a
      pandas.DataFrame.

    TODO throw error when duplicate bindings/namespaces collide
    TODO resolve query if bindings or namespaces have changed

    :param graph: the rdflib.graph.Graph to be queried
    :param initBindings: a dictionary of bindings where the key is the variable in
        the sparql string, and the value is the URI/Literal to BIND to the variable.
    :param initBindingsKwarg: kwarg version of initBindings
    :param initNs: kwarg version of initNs
    :return: pandas.DataFrame containing the contents of the SPARQL query
        result from rdflib
    """
    assert (
        cls.query or cls.sparql
    ), "No rdflib Query or SPARQL string has been set for the class."

    # note: merge method kwargs with default class bindings
    if initBindings:
        all_bindings = {**cls.classBindings, **initBindings, **initBindingsKwarg}
    else:
        all_bindings = {**cls.classBindings, **initBindingsKwarg}

    # note: merge method kwargs with default namespace
    if initNs:
        initNs = {**cls.initNs, **initNs}
    else:
        initNs = {**cls.initNs}

    # Check if query should be updated due to stale sparql string
    update_query = cls.p_sparql != cls.sparql
    if not cls.query or update_query or cls.initNs != cls.p_initNs:
        cls.query = prepareQuery(cls.sparql, initNs=initNs)
        if cls.initNs:
            cls.p_initNs = cls.initNs

    result = graph.query(cls.query, initBindings=all_bindings, initNs=initNs)

    if cls.columns is None:
        # Try to infer from query vars
        try:
            cls.columns = [str(var) for var in result.vars]
        except TypeError:
            # no columns. Probably an ASK or CONSTRUCT query
            logging.debug(
                "No columns passed, and unable to infer. "
                "Therefore, no columns were assigned to the DataFrame."
            )

    df = DataFrame(result, columns=cls.columns)

    # update low cost trait
    cls.p_sparql = cls.sparql

    if cls.index:
        return df.set_index(cls.index)
    return df
