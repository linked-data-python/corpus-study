# Extracted from MDD4REST/mdd4rest-annotator@c46839aa3d : server/src/rdflib2/extras/infixowl.py
# region: Individual._set_identifier (lines 464-484, stratum remove)
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
