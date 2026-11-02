"""Validation driver for LDCTimeComponent.make_aif_time_component.

The region mints a blank-node time component in the graph it is given, adds
its xsd:string-typed timeType (the computed typed literal of the stratum:
`Literal(self.time_type.name, datatype=XSD.string)`), and then year/month/day
through the context method add_literal (shim.py) for the values that exist.
Oracle: the graph passed in, isomorphic after the call (the blank node by its
place in the graph), and the node returned.

Calls (each on a fresh graph; the first one already holds an unrelated
triple that must survive):

* ON, full date given as strings;
* BEFORE, a full date given as integers (lexical forms "2021", "1", "5");
* UNKNOWN, a year only: no month, no day triples;
* AFTER, nothing but the type.

`xsd:string` is NOT the plain literal: Literal("ON") != Literal("ON",
datatype=XSD.string) in rdflib, so a translation binding the bare name would
be caught by the graph comparison.
"""
from rdflib import Graph, Literal, URIRef

from rdfeval.harness import run_pair
from shim import LDCTimeComponent, LDCTimeType


def _case(time_type, year, month, day, populated=False):
    def make():
        g = Graph()
        if populated:
            g.add((URIRef("http://example.org/doc"),
                   URIRef("http://example.org/note"), Literal("kept")))
        return (LDCTimeComponent(time_type, year, month, day), g), {}
    return make


VERDICT = run_pair(
    __file__,
    entry="make_aif_time_component",
    calls=[
        _case(LDCTimeType.ON, "2020", "03", "15", populated=True),
        _case(LDCTimeType.BEFORE, 2021, 1, 5),
        _case(LDCTimeType.UNKNOWN, "1999", None, None),
        _case(LDCTimeType.AFTER, None, None, None),
    ],
)
