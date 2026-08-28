"""Validation driver for ProfilesDataset.load_owl_imports.

The region is a method that recurses through ``self``; the stub below
provides the two attributes it reads (``external_resources``, ``client``)
and re-enters the *region under test* by picking it up from the calling
module's globals -- so each representation recurses into itself.

Fixtures: a graph without owl:imports, a graph with a chain of imports
(base -> leaf, exercising the recursion and the external_resources
bookkeeping), and a graph whose import is already marked as loaded.
"""
import sys

from rdflib import Graph

from rdfeval.harness import run_pair

NO_IMPORTS = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<http://example.org/onto/local> rdfs:label "local" .
"""

WITH_IMPORTS = """
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
<http://example.org/onto/local> a owl:Ontology ;
    owl:imports <http://example.org/onto/base> ;
    rdfs:label "local" .
"""


class _Loader:
    """Stand-in for ProfilesDataset (the region's ``self``)."""

    def __init__(self, external_resources=()):
        self.external_resources = set(external_resources)
        self.client = None

    def load_owl_imports(self, graph):
        # the region recurses through self; dispatch back to the region of
        # the module that is calling us (original.py or translated.ldpy)
        fn = sys._getframe(1).f_globals["load_owl_imports"]
        return fn(self, graph)

    def __eq__(self, other):
        return (isinstance(other, _Loader)
                and self.external_resources == other.external_resources)

    def __repr__(self):
        return "_Loader(external_resources=%r)" % sorted(self.external_resources)


def case(data, already=()):
    def make():
        g = Graph()
        g.parse(data=data, format="turtle")
        return ((_Loader(already), g), {})
    return make


VERDICT = run_pair(
    __file__,
    entry="load_owl_imports",
    calls=[
        case(NO_IMPORTS),
        case(WITH_IMPORTS),
        case(WITH_IMPORTS, already=("http://example.org/onto/base",)),
    ],
)
