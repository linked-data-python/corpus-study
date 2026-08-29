# Extracted from ktbs/ktbs@4f9f50c770 : lib/rdfrest/util/proxystore.py
# region: ProxyStore.query (lines 571-587, stratum bind_initbindings)
# licence of the source repository: see meta.json
def query(self, query, initNs=None, initBindings=None, queryGraph=None, 
          **kw): 
    """ I provide SPARQL query processing as a store.

    I simply pass through the query to the underlying graph. This prevents
    an external SPARQL engine to make multiple accesses to that store,
    which can generate HTTP traffic.
    """
    # initNs and initBindings are invalid names for pylint (C0103), but
    # method `query` is specified by rdflib, so #pylint: disable=C0103
    if initNs is None:
        initNs = {}
    if initBindings is None:
        initBindings = {}
    self._pull()
    return self._graph.query(query, initNs=initNs,
                             initBindings=initBindings, **kw)
