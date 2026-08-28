# Extracted from vemonet/rdflib-endpoint@1427c77829 : src/rdflib_endpoint/sparql_router.py
# region: SparqlRouter._prepare_query_cached (lines 328-343, stratum bind_initbindings)
# licence of the source repository: see meta.json
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from rdflib.plugins.sparql import CUSTOM_EVALS, prepareQuery, prepareUpdate

def _prepare_query_cached(self, query: str, graph_ns: Dict[str, Any]) -> Any:
    """Prepare a SPARQL query, reusing the parsed query for repeated requests.

    The cache key includes the graph namespaces since they are used as initNs
    (they can change when update queries add prefixes).
    """
    key = (query, frozenset((prefix, str(ns)) for prefix, ns in graph_ns.items()))
    cached = self._prepared_queries.get(key)
    if cached is not None:
        self._prepared_queries.move_to_end(key)
        return cached
    prepared = prepareQuery(query, initNs=graph_ns)
    self._prepared_queries[key] = prepared
    if len(self._prepared_queries) > 128:
        self._prepared_queries.popitem(last=False)
    return prepared
