# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : tests/unit/test_starlight_graph.py
# region: TestRdflibCompat.test_remove_triple (lines 47-50, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, BNode
EX = 'http://example.org/'

def test_remove_triple(self, sg):
    sg.add((URIRef(EX+'s'), URIRef(EX+'p'), URIRef(EX+'o')))
    sg.remove((URIRef(EX+'s'), URIRef(EX+'p'), URIRef(EX+'o')))
    assert (URIRef(EX+'s'), URIRef(EX+'p'), URIRef(EX+'o')) not in sg
