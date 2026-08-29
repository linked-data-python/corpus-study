"""Validation driver for dtai-kg__SCOOP__…__RML_removeBlankNodesMultipleMaps.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

The region is a method: it reads `self.graph` and appends its result to
`self.graphs`, so it needs the object that owns it.  `RML` below stands in for
SCOOP's own (RML.py lines 20-45 of the same commit, restricted to the
constants the region reads); one instance is built per side, around its own
copy of the fixture, and `__eq__` states the oracle: two runs agree when the
list of graph dictionaries they collected agrees graph by graph, compared by
RDF isomorphism through the harness's own `normalise`.
"""
import sys

sys.dont_write_bytecode = True

from pathlib import Path

import rdflib

from rdfeval.harness import fixture_graph, normalise, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


class RML:
    """Stands in for the SCOOP RML object that owns the method.

    Faithful to RML.__init__ (dtai-kg/SCOOP@40c6fc0420, RML.py lines 20-45)
    for everything the region reads: the two namespaces and the six term
    constants, plus `self.graph` and the `self.graphs` accumulator.
    """

    def __init__(self, graph):
        self.graph = graph
        self.rmlNS = rdflib.Namespace("http://semweb.mmlab.be/ns/rml#")
        self.r2rmlNS = rdflib.Namespace("http://www.w3.org/ns/r2rml#")
        self.POM = self.r2rmlNS.predicateObjectMap
        self.PREDICATE = self.r2rmlNS.predicate
        self.SUBJECT_MAP = self.r2rmlNS.subjectMap
        self.OJBECT_MAP = self.r2rmlNS.objectMap
        self.CONSTANT = self.r2rmlNS.constant
        self.OBJECT = self.r2rmlNS.object
        self.graphs = []

    def __eq__(self, other):
        # the observable outcome of the region: what it appended to self.graphs
        return normalise(self.graphs) == normalise(other.graphs)

    __hash__ = None


def mapping_document():
    return ((RML(fixture_graph(FIXTURE)),), {})


VERDICT = run_pair(
    __file__,
    entry="removeBlankNodesMultipleMaps",
    fixture="fixture.ttl",
    calls=[mapping_document],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
