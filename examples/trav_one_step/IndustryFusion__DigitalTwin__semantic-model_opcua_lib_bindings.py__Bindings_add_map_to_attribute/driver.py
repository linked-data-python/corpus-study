"""Driver for Bindings.add_map_to_attribute (IndustryFusion DigitalTwin).

`self` is a stand-in whose __init__ is Bindings.__init__ verbatim (bindings.py
@3b40088b88).  The region draws a random name for the map IRI: every call
seeds `random` first, so both sides draw the same one (each side runs in a
process of its own).  What is compared: the bindings graph the region writes
(self.bindingsg, isomorphism), the input graph g (unchanged), what it prints
(idtype2String's warning) and the raise (StopIteration) when a read has no
solution.
"""
import random
from pathlib import Path

from rdflib import Graph, Namespace, URIRef

from rdfeval.harness import fixture_graph, run_pair

FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"
EX = Namespace("http://example.org/")
BASENS = Namespace("https://industryfusion.github.io/contexts/ontology/v0/base/")


class Bindings:
    def __init__(self, namespace_prefix, basens):
        self.bindingsg = Graph()
        self.basens = basens
        self.binding_namespace = Namespace(f'{namespace_prefix}bindings/')
        self.bindingsg.bind('binding', self.binding_namespace)


def call(var, seed, attribute=EX.attribute, varname="var1", connector=BASENS["OPCUAConnector"],
         prefilled=False):
    def make():
        random.seed(seed)
        self = Bindings("http://example.org/entity/", BASENS)
        if prefilled:       # the write adds to a graph that already has content
            self.bindingsg.add((EX.earlier, EX.p, EX.o))
        return (self, fixture_graph(FIXTURE), attribute, varname, var, connector), {}
    return make


CALLS = [
    call(EX.var1, 1),                                       # numeric, datatype given
    call(EX.var2, 2, attribute=EX.attr2, varname="speed"),  # default anyType, string id
    call(EX.var3, 3),                                       # guid
    call(EX.var3b, 4),                                      # opaque
    call(EX.var4, 5),                                       # unknown id type: warning printed
    call(EX.var5, 6),                                       # no hasNodeId: StopIteration
    call(EX.var6, 7),                                       # no hasUri: StopIteration
    call(EX.var7, 8),                                       # several values: the first
    call(EX.unknown, 9),                                    # not in the graph: StopIteration
    call(EX.var1, 10, prefilled=True, varname="again"),     # the write adds, never replaces
]

VERDICT = run_pair(__file__, entry="add_map_to_attribute", fixture="fixture.ttl", calls=CALLS)
