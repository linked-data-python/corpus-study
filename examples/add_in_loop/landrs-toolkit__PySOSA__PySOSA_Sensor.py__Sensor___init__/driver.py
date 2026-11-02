"""Validation driver for landrs-toolkit__PySOSA__PySOSA_Sensor.py__Sensor___init__.

`Sensor.__init__` writes into the module graph `obsgraph` (the graph the whole
PySOSA package shares, `config.get_graph()`), which is not an argument: for the
comparison to see it, the stub `self` of each call carries that very graph in
`self.graph` (the harness canonicalises every argument after the call, by RDF
isomorphism, so the triples the call wrote -- and the blank node `sensor_id`
that carries them -- are compared).  The graph accumulates over the calls,
identically on both sides.

Calls (observed properties and procedures are ObservableProperty / Procedure
instances, or anything else, which the `isinstance` tests must skip):
  full         two properties, two procedures
  skipped      a property that is a plain string, a procedure that is a
               property (wrong class): neither is written
  empty        empty lists: only the three triples about the sensor
  non-text     a label and a comment that are not strings (an int, a float)
  not_iterable the properties are None: the call raises TypeError AFTER the
               three triples about the sensor are written
  too_few      one argument (IndexError at args[1], before anything is
               written) and three (IndexError at args[3], after the label and
               comment are set but before any triple)
"""
from types import SimpleNamespace

from rdfeval.harness import run_pair
import context_shim as shim

OP, PR = shim.ObservableProperty, shim.Procedure


def _call(*args):
    def make():
        return (SimpleNamespace(graph=shim.get_graph()),) + args, {}
    return make


CALLS = [
    _call("thermometer", "measures air temperature",
          [OP("temperature"), OP("humidity")], [PR("calibration"), PR("sampling")]),
    _call("barometer", "measures pressure",
          ["pressure", OP("pressure")], [OP("not-a-procedure"), PR("reading")]),
    _call("bare sensor", "no properties", [], []),
    _call(42, 1.5, [OP("count")], []),
    _call("broken", "properties are None", None, []),
    _call("short"),
    _call("short", "three args", []),
]

VERDICT = run_pair(
    __file__,
    entry='__init__',
    calls=CALLS,
)
