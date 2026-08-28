"""Validation driver for pyLODE's get_image_object.

The region reads seven properties of an image object out of a graph and
packs them into an ImageObject dataclass, so the fixtures below build small
graphs and the harness compares the returned dataclasses (and the input
graphs, which the region must leave untouched).

Context: ``get_value`` and the ImageObject/MediaObject dataclasses live in
the local ``supermodel_context.py`` shim (see its header) because pylode
itself cannot be imported in the evaluation venv.
"""
from rdflib import DCTERMS, SDO, SH, Graph, Literal, URIRef, XSD

from rdfeval.harness import run_pair

IRI = URIRef("http://example.org/img/diagram")


def _graph(triples):
    g = Graph()
    for p, o in triples:
        g.add((IRI, p, o))
    return g


def fully_described():
    g = _graph([
        (SDO.name, Literal("Component model diagram")),
        (SDO.description, Literal("An overview of the component models", lang="en")),
        (SDO.encodingFormat, Literal("image/png")),
        (DCTERMS.source, URIRef("http://example.org/source")),
        (SH.order, Literal(3, datatype=XSD.integer)),
        (SDO.contentUrl, URIRef("http://example.org/img/diagram.png")),
        (SDO.caption, Literal("Figure 1")),
    ])
    return ((IRI, g), {})


def sparsely_described():
    """Missing name/description/order exercise MediaObject.__post_init__."""
    g = _graph([
        (SDO.encodingFormat, Literal("image/svg+xml")),
        (SDO.contentUrl, URIRef("http://example.org/img/diagram.svg")),
    ])
    return ((IRI, g), {})


def empty_graph():
    return ((IRI, Graph()), {})


VERDICT = run_pair(__file__, entry="get_image_object",
                   calls=[fully_described, sparsely_described, empty_graph])
