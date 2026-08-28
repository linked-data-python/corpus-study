# Extracted from maparent/virtuoso-python@eba377e1fa : virtuoso/vstore.py
# region: Virtuoso._sparql_construct (lines 372-378, band medium)
# licence of the source repository: see meta.json
from rdflib.graph import Graph
log = logging.getLogger(__name__)

def _sparql_construct(self, q, cursor):
    log.debug("_sparql_construct")
    g = Graph()
    results = cursor.execute(q)
    for result in results:
        g.add(resolve(cursor, x) for x in result)
    return g
