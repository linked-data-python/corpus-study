# Extracted from mariocosenza/kgsum@320b14fc57 : src/dataset_preparation.py
# region: select_local_property (lines 203-227, stratum bind_initbindings)
# licence of the source repository: see meta.json
import rdflib
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("dataset_preparation")

def select_local_property(parsed_graph):
    Q_LOCAL_PROPERTY = prepareQuery("""
        SELECT ?property (COUNT(?s) AS ?usageCount)
        WHERE {
            ?s ?property ?o .
            FILTER (?property != rdf:type)
        }
        GROUP BY ?property
        ORDER BY DESC(?usageCount)
        LIMIT 1000
    """, initNs={"rdf": rdflib.RDF})
    log_query(Q_LOCAL_PROPERTY)
    try:
        qres = parsed_graph.query(Q_LOCAL_PROPERTY)
    except Exception as e:
        logger.warning(f"SPARQL error in select_local_property: {e}")
        return []

    properties = set()
    for row in qres:
        property_uri = str(row.property)
        if not property_uri:
            continue
        properties.add(property_uri)
    return list(properties)
