# Extracted from oxigraph/oxrdflib@70b1268a8e : tests/test_graph.py
# region: GraphTestCase.remove_stuff (lines 71-86, stratum remove)
# licence of the source repository: see meta.json
def remove_stuff(self) -> None:
    tarek = self.tarek
    michel = self.michel
    bob = self.bob
    likes = self.likes
    hates = self.hates
    pizza = self.pizza
    cheese = self.cheese

    self.graph.remove((tarek, likes, pizza))
    self.graph.remove((tarek, likes, cheese))
    self.graph.remove((michel, likes, pizza))
    self.graph.remove((michel, likes, cheese))
    self.graph.remove((bob, likes, cheese))
    self.graph.remove((bob, hates, pizza))
    self.graph.remove((bob, hates, michel))  # gasp!
