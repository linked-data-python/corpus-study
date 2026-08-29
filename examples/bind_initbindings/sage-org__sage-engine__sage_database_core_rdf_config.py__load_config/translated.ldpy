# Extracted from sage-org/sage-engine@4c5e8fffc0 : sage/database/core/rdf_config.py
# region: load_config (lines 118-152, stratum bind_initbindings)
# licence of the source repository: see meta.json
import logging
from sage.database.core.graph import Graph

for row in qres:
    # load basic information about the graph
    if row.name is None:
        raise SyntaxError("A valid SaGe RDF graph must have a name (declared using foaf:name)!")
    g_name = row.name
    g_description = row.desc if row.desc is not None else "Unnamed RDF graph with id {}".format(g_name)
    g_quantum = row.quantum if row.quantum is not None else quantum
    g_max_results = row.pageSize if row.pageSize is not None else max_results

    # load default queries for this graph
    # TODO
    g_queries = list()
    # g_queries = g_config["queries"] if "queries" in g_config else list()

    # load the backend for this graph
    g_connector = None
    backend_config = dict()
    backend_name = None
    # fetch backend config. parameters first
    backend_res = graph.query(backend_query, initBindings = { "backend": row.backend })
    if len(backend_res) == 0:
        logging.error(f"Graph with name '{g_name}' has a backend declared with an invalid syntax. Please check your configuration file using the documentation.")
    else:
        for b_row in backend_res:
            backend_name = str(b_row.name)
            backend_config[str(b_row.paramName)] = str(b_row.paramValue)
        # load the graph connector using available backends
        if backend_name in backends:
            g_connector = backends[backend_name](backend_config)
        else:
            logging.error(f"Impossible to find the backend with name {backend_name}, declared for the RDF Graph {g_name}")
            continue
        # build the graph and register it
        graphs[g_name] = Graph(g_name, g_description, g_connector, quantum=g_quantum, max_results=g_max_results, default_queries=g_queries)
        logging.info("RDF Graph '{}' (backend: {}) successfully loaded".format(g_name, backend_name))
