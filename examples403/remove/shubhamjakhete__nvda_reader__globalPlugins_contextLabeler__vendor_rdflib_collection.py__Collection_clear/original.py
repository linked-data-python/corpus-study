# Extracted from shubhamjakhete/nvda_reader@8b5fb51e42 : globalPlugins/contextLabeler/_vendor/rdflib/collection.py
# region: Collection.clear (lines 261-269, stratum remove)
# licence of the source repository: see meta.json
from typing import TYPE_CHECKING, Iterable, Iterator, List, Optional
from rdflib.namespace import RDF
from rdflib.term import BNode, Node

def clear(self):
    container: Optional[Node] = self.uri
    graph = self.graph
    while container:
        rest = graph.value(container, RDF.rest)
        graph.remove((container, RDF.first, None))
        graph.remove((container, RDF.rest, None))
        container = rest
    return self
