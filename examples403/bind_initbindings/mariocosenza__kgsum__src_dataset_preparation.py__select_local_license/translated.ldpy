# Extracted from mariocosenza/kgsum@320b14fc57 : src/dataset_preparation.py
# region: select_local_license (lines 264-278, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("dataset_preparation")

def select_local_license(parsed_graph):
    Q_LOCAL_DCTERMS_LICENSE = prepareQuery("""
        SELECT ?license
        WHERE {
            ?s dcterms:license ?license .
        }
        LIMIT 1
    """, initNs={"dcterms": 'http://purl.org/dc/terms/'})
    log_query(Q_LOCAL_DCTERMS_LICENSE)
    try:
        qres = parsed_graph.query(Q_LOCAL_DCTERMS_LICENSE)
    except Exception as e:
        logger.warning(f"SPARQL error in select_local_license: {e}")
        return set()
    return {str(row.license) for row in qres}
