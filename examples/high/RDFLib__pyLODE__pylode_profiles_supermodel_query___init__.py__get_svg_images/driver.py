"""Validation driver for get_svg_images.

Pure read: the region filters the ``sdo:image`` objects of one subject down
to the literal ones.  The fixtures build a graph in which the answer is a
proper subset of the objects (an IRI-valued image must be dropped) and one
in which the subject has no image at all.
"""
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import SDO

from rdfeval.harness import run_pair

EX = "http://example.org/"


def _graph():
    g = Graph()
    g.add((URIRef(EX + "a"), SDO.image, Literal("<svg id='a'/>")))
    g.add((URIRef(EX + "a"), SDO.image, URIRef(EX + "a.png")))
    g.add((URIRef(EX + "a"), SDO.image, Literal("<svg id='a2'/>")))
    g.add((URIRef(EX + "a"), SDO.name, Literal("A")))
    g.add((URIRef(EX + "b"), SDO.image, Literal("<svg id='b'/>")))
    return g


def case_documented():
    return ((URIRef(EX + "a"), _graph()), {})


def case_no_image():
    return ((URIRef(EX + "c"), _graph()), {})


VERDICT = run_pair(__file__, entry="get_svg_images",
                   calls=[case_documented, case_no_image])
