# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_graph_context.py
# region: ContextTestCase.remove_stuff (lines 77-94, stratum remove)
# licence of the source repository: see meta.json
from rdflib import BNode, ConjunctiveGraph, Graph, URIRef

def remove_stuff(self) -> None:
    tarek = self.tarek
    michel = self.michel
    bob = self.bob
    likes = self.likes
    hates = self.hates
    pizza = self.pizza
    cheese = self.cheese
    c1 = self.c1
    graph = Graph(self.graph.store, c1)

    graph.remove((tarek, likes, pizza))
    graph.remove((tarek, likes, cheese))
    graph.remove((michel, likes, pizza))
    graph.remove((michel, likes, cheese))
    graph.remove((bob, likes, cheese))
    graph.remove((bob, hates, pizza))
    graph.remove((bob, hates, michel))  # gasp!
