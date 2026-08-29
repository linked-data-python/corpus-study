# Extracted from mariocosenza/kgsum@320b14fc57 : src/dataset_preparation.py
# region: select_local_endpoint (lines 230-244, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("dataset_preparation")

def select_local_endpoint(parsed_graph):
    Q_LOCAL_VOID_SPARQL = prepareQuery("""
        SELECT DISTINCT ?o
        WHERE {
            ?s void:sparqlEndpoint ?o .
        }
        LIMIT 2
    """, initNs={"void": 'http://rdfs.org/ns/void#'})
    log_query(Q_LOCAL_VOID_SPARQL)
    try:
        qres = parsed_graph.query(Q_LOCAL_VOID_SPARQL)
    except Exception as e:
        logger.warning(f"SPARQL error in select_local_endpoint: {e}")
        return []
    return list({str(row.o) for row in qres})
