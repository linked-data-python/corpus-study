# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Property.__init__ (lines 1932-1958, band medium)
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
from rdflib.util import first
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def __init__(
    self, identifier=None, graph=None, baseType=OWL_NS.ObjectProperty,
    subPropertyOf=None, domain=None, range=None, inverseOf=None,
    otherType=None, equivalentProperty=None,
    comment=None,
    verbAnnotations=None,
    nameAnnotation=None,
        nameIsLabel=False):
    super(Property, self).__init__(identifier, graph,
                                   nameAnnotation, nameIsLabel)
    if verbAnnotations:
        self.setupVerbAnnotations(verbAnnotations)

    assert not isinstance(self.identifier, BNode)
    if baseType is None:
        # None give, determine via introspection
        self._baseType = first(
            Individual(self.identifier, graph=self.graph).type)
    else:
        if (self.identifier, RDF.type, baseType) not in self.graph:
            self.graph.add((self.identifier, RDF.type, baseType))
        self._baseType = baseType
    self.subPropertyOf = subPropertyOf
    self.inverseOf = inverseOf
    self.domain = domain
    self.range = range
    self.comment = comment and comment or []
