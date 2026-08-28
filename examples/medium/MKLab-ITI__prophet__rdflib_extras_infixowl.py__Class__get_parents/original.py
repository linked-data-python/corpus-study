# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Class._get_parents (lines 1151-1200, band medium)
# licence of the source repository: see meta.json
import itertools
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
from infixowl_ctx import (  # context shim, see infixowl_ctx.py
    Class, Individual, OWLRDFListProxy)
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

def _get_parents(self):
    """
    computed attributes that returns a generator over taxonomic 'parents'
    by disjunction, conjunction, and subsumption

    >>> from rdflib.util import first
    >>> exNs = Namespace('http://example.com/')
    >>> namespace_manager = NamespaceManager(Graph())
    >>> namespace_manager.bind('ex', exNs, override=False)
    >>> namespace_manager.bind('owl', OWL_NS, override=False)
    >>> g = Graph()
    >>> g.namespace_manager = namespace_manager
    >>> Individual.factoryGraph = g
    >>> brother = Class(exNs.Brother)
    >>> sister = Class(exNs.Sister)
    >>> sibling = brother | sister
    >>> sibling.identifier = exNs.Sibling
    >>> sibling #doctest: +SKIP
    ( ex:Brother OR ex:Sister )
    >>> first(brother.parents) #doctest: +SKIP
    Class: ex:Sibling EquivalentTo: ( ex:Brother OR ex:Sister )
    >>> parent = Class(exNs.Parent)
    >>> male = Class(exNs.Male)
    >>> father = parent & male
    >>> father.identifier = exNs.Father
    >>> list(father.parents) #doctest: +SKIP
    [Class: ex:Parent , Class: ex:Male ]

    """
    for parent in itertools.chain(self.subClassOf,
                                  self.equivalentClass):
        yield parent

    link = first(self.factoryGraph.subjects(RDF.first, self.identifier))
    if link:
        listSiblings = list(self.factoryGraph.transitive_subjects(RDF.rest,
                                                                  link))
        if listSiblings:
            collectionHead = listSiblings[-1]
        else:
            collectionHead = link
        for disjCls in self.factoryGraph.subjects(
                OWL_NS.unionOf, collectionHead):
            if isinstance(disjCls, URIRef):
                yield Class(disjCls, skipOWLClassMembership=True)
    for rdfList in self.factoryGraph.objects(
            self.identifier, OWL_NS.intersectionOf):
        for member in OWLRDFListProxy([rdfList], graph=self.factoryGraph):
            if isinstance(member, URIRef):
                yield Class(member, skipOWLClassMembership=True)

# --- demo harness: identical in original.py and translated.ldpy ---
# _get_parents is a generator over a graph; the demo rebuilds the situation of
# its own docstring (a union class and an intersection class) and compares the
# pair on demo_graph + stdout.
from rdflib import Graph

demo_graph = Graph()
Individual.factoryGraph = demo_graph
exNs = Namespace('http://example.com/')
brother = Class(exNs.Brother)
sister = Class(exNs.Sister)
sibling = brother | sister
sibling.identifier = exNs.Sibling
parent = Class(exNs.Parent)
male = Class(exNs.Male)
father = parent & male
father.identifier = exNs.Father
brother.subClassOf = [Class(exNs.Person)]
print(sorted(str(p.identifier) for p in _get_parents(brother)))
print(sorted(str(p.identifier) for p in _get_parents(father)))
