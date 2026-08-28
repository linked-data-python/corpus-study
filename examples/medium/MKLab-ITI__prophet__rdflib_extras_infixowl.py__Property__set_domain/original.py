# Extracted from MKLab-ITI/prophet@eee2ab51de : rdflib/extras/infixowl.py
# region: Property._set_domain (lines 2084-2093, band medium)
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
from rdflib.term import Identifier
from infixowl_ctx import (  # context shim, see infixowl_ctx.py
    Class, Individual, Property, classOrIdentifier)

def _set_domain(self, other):
    if not other:
        return
    if isinstance(other, (Individual, Identifier)):
        self.graph.add(
            (self.identifier, RDFS.domain, classOrIdentifier(other)))
    else:
        for dom in other:
            self.graph.add(
                (self.identifier, RDFS.domain, classOrIdentifier(dom)))

# --- demo harness: identical in original.py and translated.ldpy ---
# The region is a property setter that mutates self.graph; it is exercised on
# a real infixowl Property and the pair compared on demo_graph + stdout.
from rdflib import Graph

Individual.factoryGraph = Graph()
demo_graph = Graph()
prop = Property(URIRef("http://example.com/hasName"), graph=demo_graph)
_set_domain(prop, URIRef("http://example.com/Person"))          # single term
_set_domain(prop, [URIRef("http://example.com/A"),              # iterable
                   Class(URIRef("http://example.com/B"), graph=demo_graph)])
_set_domain(prop, None)                                          # early return
print(len(demo_graph),
      sorted(str(o) for o in demo_graph.objects(None, RDFS.domain)))
