# Extracted from MDD4REST/mdd4rest-annotator@c46839aa3d : server/src/rdflib2/extras/infixowl.py
# region: Individual._set_identifier (lines 464-484, stratum remove)
# licence of the source repository: see meta.json
from rdflib import BNode

def _set_identifier(self, i):
    assert i
    if i != self.__identifier:
        oldStmtsOut = list(self.graph.predicate_objects(self.__identifier))
        oldStmtsIn = list(self.graph.subject_predicates(self.__identifier))
        self.graph.remove((self.__identifier, None, None))
        self.graph.remove((None, None, self.__identifier))
        self.__identifier = i
        self.graph += [(i, p1, o1) for p1, o1 in oldStmtsOut]
        self.graph += [(s1, p1, i) for s1, p1 in oldStmtsIn]
    if not isinstance(i, BNode):
        try:
            prefix, uri, localName = self.graph.compute_qname(i)
            self.qname = u':'.join([prefix, localName])
        except:
            pass
