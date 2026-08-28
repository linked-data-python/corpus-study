# Extracted from maparent/virtuoso-python@eba377e1fa : virtuoso/tests/test_mapping.py
# region: TestMapping.test_05b_declare_quads_and_link (lines 185-196, band medium)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace
session = Session(autocommit=False)
TST = Namespace('http://example.com/test#')

def test_05b_declare_quads_and_link(self):
    qs, g, cpe = self.create_qs_graph()
    td_iri = cpe.iri_accessor(D)
    print(self.declare_qs_graph(qs))
    a = A()
    d = D()
    d.a = a
    session.add(d)
    session.add(a)
    session.commit()
    graph = Graph(self.store, identifier=self.graphname)
    assert list(graph.triples((None, TST.alink, None)))
