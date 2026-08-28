# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class.__init__ (lines 946-969, band medium)
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
from rdflib.extras.infixowl import Class   # context shim, see meta.json
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def __init__(self, identifier=None, subClassOf=None, equivalentClass=None,
             disjointWith=None, complementOf=None, graph=None,
             skipOWLClassMembership=False, comment=None,
             nounAnnotations=None,
             nameAnnotation=None,
             nameIsLabel=False):
    super(Class, self).__init__(identifier, graph,
                                nameAnnotation, nameIsLabel)

    if nounAnnotations:
        self.setupNounAnnotations(nounAnnotations)
    if not skipOWLClassMembership \
            and (self.identifier, RDF.type, OWL_NS.Class) \
            not in self.graph and \
            (self.identifier, RDF.type, OWL_NS.Restriction) \
            not in self.graph:
        self.graph.add((self.identifier, RDF.type, OWL_NS.Class))

    self.subClassOf = subClassOf and subClassOf or []
    self.equivalentClass = equivalentClass and equivalentClass or []
    self.disjointWith = disjointWith and disjointWith or []
    if complementOf:
        self.complementOf = complementOf
    self.comment = comment and comment or []
