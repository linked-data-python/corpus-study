# Extracted from statnett/KGraphPy@38859be62f : kgraphpy/header.py
# region: CIMMetadataHeader.remove_triple (lines 343-351, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, Node, URIRef, RDF, BNode, Literal
from typing import Iterable, List, Tuple, Optional, Set

def remove_triple(self, predicate: Node, obj: Optional[Node] = None):
    """Remove metadata triples matching predicate (and optionally object).
    Untested method.
    """
    if obj is None:
        for (_, _, o) in list(self.graph.triples((self.subject, predicate, None))):
            self.graph.remove((self.subject, predicate, o))
    else:
        self.graph.remove((self.subject, predicate, obj))
