# Context shim (see meta.json): the part of the PySOSA package that
# PySOSA/Sensor.py (landrs-toolkit/PySOSA@1993668bd7) imports, so that
# Sensor.__init__ executes outside the package.
#
#   * `config` (PySOSA/config.py): the module-level graph all the PySOSA
#     classes write into, returned by get_graph(), and the SOSA namespace.
#   * `ObservableProperty`, `Procedure`: reduced to the one attribute the
#     region reads, `label` (the real classes also register themselves in the
#     graph; this region never reaches that).
#
# Identical bindings for both representations.
import types

from rdflib import Graph, Literal, Namespace

sosa = Namespace("http://www.w3.org/ns/sosa/")

_graph = Graph()


def get_graph():
    return _graph


config = types.SimpleNamespace(get_graph=get_graph, sosa=sosa)


class ObservableProperty:
    def __init__(self, label):
        self.label = Literal(label)


class Procedure:
    def __init__(self, label):
        self.label = Literal(label)
