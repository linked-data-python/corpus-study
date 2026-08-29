# Extracted from shubhamjakhete/nvda_reader@8b5fb51e42 : globalPlugins/contextLabeler/_vendor/rdflib/collection.py
# region: Collection._end (lines 211-219, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF
from rdflib.term import BNode, Node

def _end(self) -> Node:
    # find end of list
    container = self.uri
    while True:
        rest = self.graph.value(container, RDF.rest)
        if rest is None or rest == RDF.nil:
            return container
        else:
            container = rest
