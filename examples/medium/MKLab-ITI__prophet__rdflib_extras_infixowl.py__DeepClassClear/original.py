# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: DeepClassClear (lines 772-839, band medium)
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
from infixowl_shim import (
    BooleanClass,
    CastClass,
    Class,
    Individual,
    classOrIdentifier,
    some,
)
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def DeepClassClear(classToPrune):
    """
    Recursively clear the given class, continuing
    where any related class is an anonymous class

    >>> EX = Namespace('http://example.com/')
    >>> namespace_manager = NamespaceManager(Graph())
    >>> namespace_manager.bind('ex', EX, override=False)
    >>> namespace_manager.bind('owl', OWL_NS, override=False)
    >>> g = Graph()
    >>> g.namespace_manager = namespace_manager
    >>> Individual.factoryGraph = g
    >>> classB = Class(EX.B)
    >>> classC = Class(EX.C)
    >>> classD = Class(EX.D)
    >>> classE = Class(EX.E)
    >>> classF = Class(EX.F)
    >>> anonClass = EX.someProp | some | classD #doctest: +SKIP
    >>> classF += anonClass #doctest: +SKIP
    >>> list(anonClass.subClassOf) #doctest: +SKIP
    [Class: ex:F ]
    >>> classA = classE | classF | anonClass #doctest: +SKIP
    >>> classB += classA #doctest: +SKIP
    >>> classA.equivalentClass = [Class()] #doctest: +SKIP
    >>> classB.subClassOf = [EX.someProp | some | classC] #doctest: +SKIP
    >>> classA #doctest: +SKIP
    ( ex:E OR ex:F OR ( ex:someProp SOME ex:D ) )
    >>> DeepClassClear(classA) #doctest: +SKIP
    >>> classA #doctest: +SKIP
    (  )
    >>> list(anonClass.subClassOf) #doctest: +SKIP
    []
    >>> classB #doctest: +SKIP
    Class: ex:B SubClassOf: ( ex:someProp SOME ex:C )

    >>> otherClass = classD | anonClass #doctest: +SKIP
    >>> otherClass #doctest: +SKIP
    ( ex:D OR ( ex:someProp SOME ex:D ) )
    >>> DeepClassClear(otherClass) #doctest: +SKIP
    >>> otherClass #doctest: +SKIP
    (  )
    >>> otherClass.delete() #doctest: +SKIP
    >>> list(g.triples((otherClass.identifier, None, None))) #doctest: +SKIP
    []
    """
    def deepClearIfBNode(_class):
        if isinstance(classOrIdentifier(_class), BNode):
            DeepClassClear(_class)
    classToPrune = CastClass(classToPrune, Individual.factoryGraph)
    for c in classToPrune.subClassOf:
        deepClearIfBNode(c)
    classToPrune.graph.remove((classToPrune.identifier, RDFS.subClassOf, None))
    for c in classToPrune.equivalentClass:
        deepClearIfBNode(c)
    classToPrune.graph.remove(
        (classToPrune.identifier, OWL_NS.equivalentClass, None))
    inverseClass = classToPrune.complementOf
    if inverseClass:
        classToPrune.graph.remove(
            (classToPrune.identifier, OWL_NS.complementOf, None))
        deepClearIfBNode(inverseClass)
    if isinstance(classToPrune, BooleanClass):
        for c in classToPrune:
            deepClearIfBNode(c)
        classToPrune.clear()
        classToPrune.graph.remove((classToPrune.identifier,
                                   classToPrune._operator,
                                   None))

# --- demo harness, added identically to both representations (see meta.json).
# DeepClassClear reads Individual.factoryGraph, a module-level attribute shared
# by both runs, so it cannot be set up from a driver fixture (the harness builds
# both fixtures before calling either side).  The scenario below is the one from
# the region's own docstring; it leaves the pruned graph in a module-level
# variable the harness can compare.
from rdflib import Graph

EX = Namespace('http://example.com/')
demo_graph = Graph()
demo_graph.bind('ex', EX, override=False)
Individual.factoryGraph = demo_graph
classB = Class(EX.B)
classC = Class(EX.C)
classD = Class(EX.D)
classE = Class(EX.E)
classF = Class(EX.F)
anonClass = EX.someProp @ some @ classD
classF += anonClass
classA = classE | classF | anonClass
classB += classA
classA.equivalentClass = [Class(EX.G)]
classB.subClassOf = [EX.someProp @ some @ classC]
print('before', len(demo_graph))
DeepClassClear(classA)
print('after', len(demo_graph))
print(repr(classB))
print(sorted(str(p) for p in set(demo_graph.predicates())))
