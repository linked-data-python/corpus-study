# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: BooleanClass.__init__ (lines 1493-1513, band medium)
# licence of the source repository: see meta.json
from rdflib.collection import Collection
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def __init__(self, identifier=None, operator=OWL_NS.intersectionOf,
             members=None, graph=None):
    if operator is None:
        props = []
        for s, p, o in graph.triples_choices((identifier,
                                              [OWL_NS.intersectionOf,
                                             OWL_NS.unionOf],
                                             None)):
            props.append(p)
            operator = p
        assert len(props) == 1, repr(props)
    Class.__init__(self, identifier, graph=graph)
    assert operator in [OWL_NS.intersectionOf,
                        OWL_NS.unionOf], str(operator)
    self._operator = operator
    rdfList = list(
        self.graph.objects(predicate=operator, subject=self.identifier))
    assert not members or not rdfList, \
        "This is a previous boolean class description!" + \
        repr(Collection(self.graph, rdfList[0]).n3())
    OWLRDFListProxy.__init__(self, rdfList, members)
