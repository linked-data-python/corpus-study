# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Individual._set_identifier (lines 458-478, band medium)
# licence of the source repository: see meta.json
from rdflib import (
    BNode,
    Literal,
    Namespace,
    RDF,
    RDFS,
    URIRef,
    Variable
)

def _set_identifier(self, i):
    assert i
    if i != self.__identifier:
        oldStmtsOut = [(p, o) for s, p, o in self.graph.triples(
            (self.__identifier, None, None))]
        oldStmtsIn = [(s, p) for s, p, o in self.graph.triples(
            (None, None, self.__identifier))]
        for p1, o1 in oldStmtsOut:
            self.graph.remove((self.__identifier, p1, o1))
        for s1, p1 in oldStmtsIn:
            self.graph.remove((s1, p1, self.__identifier))
        self.__identifier = i
        self.graph.addN(
            [(i, p1, o1, self.graph) for p1, o1 in oldStmtsOut])
        self.graph.addN([(s1, p1, i, self.graph) for s1, p1 in oldStmtsIn])
    if not isinstance(i, BNode):
        try:
            prefix, uri, localName = self.graph.compute_qname(i)
            self.qname = u':'.join([prefix, localName])
        except:
            pass
