# Extracted from mariocosenza/kgsum@320b14fc57 : src/dataset_preparation.py
# region: select_local_void_description (lines 320-334, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("dataset_preparation")

def select_local_void_description(parsed_graph):
    Q_LOCAL_DCTERMS_DESCRIPTION = prepareQuery("""
        SELECT ?desc
        WHERE {
            ?s dcterms:description ?desc .
        }
        LIMIT 100
    """, initNs={"dcterms": 'http://purl.org/dc/terms/'})
    log_query(Q_LOCAL_DCTERMS_DESCRIPTION)
    try:
        qres = parsed_graph.query(Q_LOCAL_DCTERMS_DESCRIPTION)
    except Exception as e:
        logger.warning(f"SPARQL error in select_local_void_description: {e}")
        return set()
    return {str(row.desc) for row in qres}
