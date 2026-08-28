# Extracted from maparent/virtuoso-python@eba377e1fa : virtuoso/vstore.py
# region: Virtuoso.contexts (lines 457-470, band medium)
# licence of the source repository: see meta.json
from rdflib.graph import Graph
from rdflib.term import URIRef, BNode, Literal, Variable

def contexts(self, statement=None):
    if statement is None and self.quad_storage is None:
        q = u'SELECT DISTINCT __ro2sq(G) FROM RDF_QUAD'
    else:
        statement = statement or (None, None, None)
        q = (u'SELECT DISTINCT ?g WHERE '
             u'{ GRAPH ?g { %(S)s %(P)s %(O)s } }')
        q = q % _query_bindings(statement)
        if self.quad_storage:
            q = 'DEFINE input:storage %s %s' % (self.quad_storage.n3(), q)
        q = 'SPARQL '+q
    with self.cursor() as c:
        for uri, in c.execute(q):
            yield Graph(self, URIRef(uri))
