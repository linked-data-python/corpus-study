# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: CastClass (lines 850-885, band medium)
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
from infixowl_shim import (  # context shim, see meta.json
    BooleanClass,
    Class,
    EnumeratedClass,
    MalformedClass,
    Restriction,
    classOrIdentifier,
)
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def CastClass(c, graph=None):
    graph = graph is None and c.factoryGraph or graph
    for kind in graph.objects(subject=classOrIdentifier(c),
                              predicate=RDF.type):
        if kind == OWL_NS.Restriction:
            kwArgs = {'identifier': classOrIdentifier(c),
                      'graph': graph}
            for s, p, o in graph.triples((classOrIdentifier(c),
                                          None,
                                          None)):
                if p != RDF.type:
                    if p == OWL_NS.onProperty:
                        kwArgs['onProperty'] = o
                    else:
                        if p not in Restriction.restrictionKinds:
                            continue
                        kwArgs[str(p.split(OWL_NS)[-1])] = o
            if not set([str(i.split(OWL_NS)[-1])
                        for i in Restriction.restrictionKinds]
                       ).intersection(kwArgs):
                raise MalformedClass("Malformed owl:Restriction")
            return Restriction(**kwArgs)
        else:
            for s, p, o in graph.triples_choices((classOrIdentifier(c),
                                                  [OWL_NS.intersectionOf,
                                                 OWL_NS.unionOf,
                                                 OWL_NS.oneOf],
                                                  None)):
                if p == OWL_NS.oneOf:
                    return EnumeratedClass(classOrIdentifier(c), graph=graph)
                else:
                    return BooleanClass(
                        classOrIdentifier(c), operator=p, graph=graph)
            # assert (classOrIdentifier(c),RDF.type,OWL_NS.Class) in graph
            return Class(
                classOrIdentifier(c), graph=graph, skipOWLClassMembership=True)
