"""Driver for ksahlmann__myno__myno-bridge_yang_generator_rdflib.py__parseDevices.

The region reads a graph, folds every solution of its SELECT into one dict
(the sets of functionalities, services and properties, and the @id of the
last device seen) and appends that dict to the list it is given.  Compared:
the returned list, the mutation of the list passed in, and the stdout (the
`parseDevices` banner, one line per solution, the dict).

  fixture.ttl      two complete devices (a product of 2x2x2 solutions for one,
                   1 for the other), plus neighbours that must not match: an
                   incomplete device, a device of another class, a Device with
                   the predicates in the wrong namespace, an untyped subject.
  only_decoys      the same neighbours alone: zero solution, the dict holds
                   three empty lists and no @id.
  single           one device with one of each: one solution.
  prefilled_list   the list already holds a dict: the region appends to it.
  empty_graph      an empty graph.

The row order of a store is not promised (and the @id is the last device's), so
the fixture run compares as multisets, the stdout lines included being a
sequence of the same text on both sides.
"""
from rdfeval.harness import fixture_graph, run_pair
from rdflib import Graph
from pathlib import Path

HERE = Path(__file__).resolve().parent
HEAD = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix base: <http://yang-netconf-mqtt#> .
@prefix onem2m: <http://www.onem2m.org/ontology/Base_Ontology/base_ontology#> .
@prefix ex: <http://example.org/> .
"""

DECOYS = """
ex:fan a onem2m:Device ; onem2m:hasFunctionality ex:spin ; onem2m:hasService ex:spinService .
ex:sensorBox a onem2m:Sensor ; onem2m:hasFunctionality ex:f ; onem2m:hasService ex:s ;
    onem2m:hasThingProperty ex:p .
ex:ghost a onem2m:Device ; base:hasFunctionality ex:f ; base:hasService ex:s ;
    base:hasThingProperty ex:p .
"""

SINGLE = """
ex:lamp a onem2m:Device ; onem2m:hasFunctionality ex:switch ;
    onem2m:hasService ex:switchService ; onem2m:hasThingProperty ex:power .
"""


def _graph(text):
    return Graph().parse(data=HEAD + text, format="turtle")


CALLS = [
    lambda: ((fixture_graph(HERE / "fixture.ttl"), []), {}),
    lambda: ((_graph(DECOYS), []), {}),
    lambda: ((_graph(SINGLE), []), {}),
    lambda: ((fixture_graph(HERE / "fixture.ttl"), [{"@id": "earlier"}]), {}),
    lambda: ((Graph(), []), {}),
]

VERDICT = run_pair(
    __file__,
    entry='parseDevices',
    fixture="fixture.ttl",
    calls=CALLS,
)
