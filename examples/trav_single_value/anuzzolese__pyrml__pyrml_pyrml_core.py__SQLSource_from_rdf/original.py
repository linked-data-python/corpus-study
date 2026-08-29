# Extracted from anuzzolese/pyrml@d18fe2edfc : pyrml/pyrml_core.py
# region: SQLSource.from_rdf (lines 2040-2057, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import URIRef, Graph, IdentifiedNode
from rdflib.namespace import RDF, Namespace, XSD

@staticmethod
def from_rdf(g: Graph, parent: IdentifiedNode) -> Source:

    d2rq = Namespace('http://www.wiwiss.fu-berlin.de/suhl/bizer/D2RQ/0.1#')

    dsn = g.value(parent, d2rq.jdbcDSN, None, True)
    username = g.value(parent, d2rq.username, None, True)
    password = g.value(parent, d2rq.password, None, True)
    if dsn and username and password:

        driver = g.value(parent, d2rq.jdbcDriver, None, True)
        result_size_limit = g.value(parent, d2rq.resultSizeLimit, None, True)
        fetch_size = g.value(parent, d2rq.fetchSize, None, True)

        return SQLSource(parent, dsn, dsn=dsn, driver=driver, username=username, password=password, result_size_limit=result_size_limit, fetch_size=fetch_size)

    else:
        return None
