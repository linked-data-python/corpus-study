# Extracted from shubhamjakhete/nvda_reader@8b5fb51e42 : globalPlugins/contextLabeler/_vendor/rdflib/extras/infixowl.py
# region: Class._get_parents (lines 1256-1300, stratum trav_one_step)
# licence of the source repository: see meta.json
import itertools
from rdflib.namespace import OWL, RDF, RDFS, XSD, Namespace, NamespaceManager
from rdflib.term import BNode, Identifier, Literal, URIRef, Variable
from rdflib.util import first

def _get_parents(self):
    """
    computed attributes that returns a generator over taxonomic 'parents'
    by disjunction, conjunction, and subsumption

    >>> from rdflib.util import first
    >>> exNs = Namespace('http://example.com/')
    >>> g = Graph()
    >>> g.bind("ex", exNs, override=False)
    >>> Individual.factoryGraph = g
    >>> brother = Class(exNs.Brother)
    >>> sister = Class(exNs.Sister)
    >>> sibling = brother | sister
    >>> sibling.identifier = exNs.Sibling
    >>> sibling
    ( ex:Brother OR ex:Sister )
    >>> first(brother.parents)
    Class: ex:Sibling EquivalentTo: ( ex:Brother OR ex:Sister )
    >>> parent = Class(exNs.Parent)
    >>> male = Class(exNs.Male)
    >>> father = parent & male
    >>> father.identifier = exNs.Father
    >>> list(father.parents)
    [Class: ex:Parent , Class: ex:Male ]

    """
    for parent in itertools.chain(self.subClassOf, self.equivalentClass):
        yield parent

    link = first(self.factoryGraph.subjects(RDF.first, self.identifier))
    if link:
        siblingslist = list(self.factoryGraph.transitive_subjects(RDF.rest, link))
        if siblingslist:
            collectionhead = siblingslist[-1]
        else:
            collectionhead = link
        for disjointclass in self.factoryGraph.subjects(
            OWL.unionOf, collectionhead
        ):
            if isinstance(disjointclass, URIRef):
                yield Class(disjointclass, skipOWLClassMembership=True)
    for rdf_list in self.factoryGraph.objects(self.identifier, OWL.intersectionOf):
        for member in OWLRDFListProxy([rdf_list], graph=self.factoryGraph):
            if isinstance(member, URIRef):
                yield Class(member, skipOWLClassMembership=True)
