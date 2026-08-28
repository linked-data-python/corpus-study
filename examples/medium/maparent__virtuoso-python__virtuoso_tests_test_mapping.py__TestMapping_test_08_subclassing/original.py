# Extracted from maparent/virtuoso-python@eba377e1fa : virtuoso/tests/test_mapping.py
# region: TestMapping.test_08_subclassing (lines 243-259, band medium)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace
from virtuoso.vmapping import (
    VirtuosoQuadMapPattern, VirtuosoPatternIriClass, QuadStorage, VirtuosoGraphQuadMapPattern)
session = Session(autocommit=False)
TST = Namespace('http://example.com/test#')

def test_08_subclassing(self):
    qs, g, cpe = self.create_qs_graph()
    tb_iri = cpe.iri_accessor(B)
    cpe.add_pattern(
        C, VirtuosoQuadMapPattern(
            tb_iri.apply(C.id),
            TST.cname,
            C.name),
        g)
    print(self.declare_qs_graph(qs))
    b = B(name='b1')
    c = C(name='c1')
    session.add(b)
    session.add(c)
    session.commit()
    graph = Graph(self.store, identifier=self.graphname)
    assert 1 == len(list(graph.triples((None, TST.cname, None))))
