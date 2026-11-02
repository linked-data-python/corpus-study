"""Validation driver for pyscal__atomRDF__atomrdf_datamodels_workflow_workflow.py__Simulation_to_graph_calculated_properties.

The region links, for each calculated property of a simulation, the property
to the simulation (`asmo:wasCalculatedBy`) and the samples it is associated
with to the property (`asmo:hasCalculatedProperty`), and prints each sample
id.  It mutates `graph` and writes to stdout: both are compared.

`Param` stands for the calculated-property models of atomrdf: `to_graph`
writes the property's own node into the graph (here, a label) and returns its
URI.  The calls:
  two_params       two properties; the first associated with two samples (one
                   given as a string, one as a URIRef), the second with one
  no_samples       a property whose `associate_to_sample` is empty, and one
                   where it is None: only `wasCalculatedBy` is written
  none_at_all      `calculated_property` is None, then [] : nothing is
                   written, `to_graph` is not called
  prefilled        a graph that already holds a triple of the same predicate,
                   which must stay, next to the new ones
  shared_sample    two properties associated with the same sample: two
                   distinct `hasCalculatedProperty` triples on one subject
"""
from types import SimpleNamespace

from rdflib import Graph, Literal, RDFS, URIRef

from rdfeval.harness import run_pair

SIM = URIRef("http://example.org/simulation/s1")
EX = "http://example.org/"


class Param:
    def __init__(self, name, samples):
        self.name = name
        self.associate_to_sample = samples

    def to_graph(self, graph):
        uri = URIRef(EX + "property/" + self.name)
        graph.add((uri, RDFS.label, Literal(self.name)))
        return uri


def _call(params, graph=None):
    def make():
        g = graph() if graph else Graph()
        return (SimpleNamespace(calculated_property=params), g, SIM), {}
    return make


def _prefilled():
    g = Graph()
    g.add((URIRef(EX + "sample/old"),
           URIRef("http://purls.helmholtz-metadaten.de/asmo/hasCalculatedProperty"),
           URIRef(EX + "property/old")))
    return g


CALLS = [
    _call([Param("energy", [EX + "sample/a", URIRef(EX + "sample/b")]),
           Param("volume", [EX + "sample/c"])]),                      # two_params
    _call([Param("pressure", []), Param("stress", None)]),            # no_samples
    _call(None),                                                      # none_at_all
    _call([]),                                                        # none_at_all
    _call([Param("energy", [EX + "sample/a"])], graph=_prefilled),    # prefilled
    _call([Param("energy", [EX + "sample/a"]),
           Param("volume", [EX + "sample/a"])]),                      # shared_sample
]

VERDICT = run_pair(
    __file__,
    entry='to_graph_calculated_properties',
    calls=CALLS,
)
