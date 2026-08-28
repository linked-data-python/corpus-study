# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Restriction.__init__ (lines 1610-1655, band medium)
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
from rdflib.graph import Graph
from rdflib.term import Identifier
from rdflib.util import first
from infixowl_context import (
    Class, Restriction, classOrIdentifier, propertyOrIdentifier)
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def __init__(self,
             onProperty,
             graph=Graph(),
             allValuesFrom=None,
             someValuesFrom=None,
             value=None,
             cardinality=None,
             maxCardinality=None,
             minCardinality=None,
             identifier=None):
    super(Restriction, self).__init__(identifier,
                                      graph=graph,
                                      skipOWLClassMembership=True)
    if (self.identifier,
        OWL_NS.onProperty,
            propertyOrIdentifier(onProperty)) not in graph:
        graph.add((self.identifier, OWL_NS.onProperty,
                  propertyOrIdentifier(onProperty)))
    self.onProperty = onProperty
    restrTypes = [
        (allValuesFrom, OWL_NS.allValuesFrom),
        (someValuesFrom, OWL_NS.someValuesFrom),
        (value, OWL_NS.hasValue),
        (cardinality, OWL_NS.cardinality),
        (maxCardinality, OWL_NS.maxCardinality),
        (minCardinality, OWL_NS.minCardinality)]
    validRestrProps = [(i, oTerm) for (i, oTerm) in restrTypes if i]
    assert len(validRestrProps)
    restrictionRange, restrictionType = validRestrProps.pop()
    self.restrictionType = restrictionType
    if isinstance(restrictionRange, Identifier):
        self.restrictionRange = restrictionRange
    elif isinstance(restrictionRange, Class):
        self.restrictionRange = classOrIdentifier(restrictionRange)
    else:
        self.restrictionRange = first(self.graph.objects(self.identifier,
                                                         restrictionType))
    if (self.identifier,
        restrictionType,
            self.restrictionRange) not in self.graph:
        self.graph.add(
            (self.identifier, restrictionType, self.restrictionRange))
    assert self.restrictionRange is not None, Class(self.identifier)
    if (self.identifier, RDF.type, OWL_NS.Restriction) not in self.graph:
        self.graph.add((self.identifier, RDF.type, OWL_NS.Restriction))
        self.graph.remove((self.identifier, RDF.type, OWL_NS.Class))
