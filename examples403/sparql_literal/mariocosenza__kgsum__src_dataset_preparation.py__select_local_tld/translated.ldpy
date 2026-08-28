# Extracted from mariocosenza/kgsum@320b14fc57 : src/dataset_preparation.py
# region: select_local_tld (lines 173-200, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("dataset_preparation")

def select_local_tld(parsed_graph):
    Q_LOCAL_TLD = prepareQuery("""
        SELECT DISTINCT ?o
        WHERE {
            ?s ?p ?o .
            FILTER(isIRI(?o))
        }
        LIMIT 1000
    """)
    log_query(Q_LOCAL_TLD)
    try:
        qres = parsed_graph.query(Q_LOCAL_TLD)
    except Exception as e:
        logger.warning(f"SPARQL error in select_local_tld: {e}")
        return set()

    tlds = set()
    for row in qres:
        url = str(row.o)
        if url.startswith(("http://", "https://")):
            try:
                host = url.split("/")[2]
                tld = host.split(".")[-1]
                if 1 < len(tld) <= 10:
                    tlds.add(tld)
            except Exception as exc:
                logger.warning(f"Unable to parse TLD from {url}: {exc}")
    return tlds
