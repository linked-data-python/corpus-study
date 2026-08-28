"""Validation driver: get_images(iri, graph) reads image descriptions.

Fixtures follow the shape documented in the region's own docstring (a
schema.org ImageObject hanging off a subject), plus the degenerate cases:
no image at all, and an image with only some of the properties set.
"""
from rdflib import BNode, Graph, Literal, Namespace, URIRef, XSD
from rdflib.namespace import DCTERMS, RDF, SDO, SH, SKOS

from rdfeval.harness import run_pair

EX = Namespace("http://example.org/")


def _image(g, node, caption, order, url, name=None, fmt=None, source=None,
           description=None):
    g.add((EX.CSD, SDO.image, node))
    g.add((node, RDF.type, SDO.ImageObject))
    g.add((node, SDO.caption, Literal(caption)))
    g.add((node, SH.order, Literal(order)))
    g.add((node, SDO.contentUrl, Literal(url, datatype=XSD.anyURI)))
    if name is not None:
        g.add((node, SDO.name, Literal(name)))
    if fmt is not None:
        g.add((node, SDO.encodingFormat, Literal(fmt)))
    if source is not None:
        g.add((node, DCTERMS.source, Literal(source)))
    if description is not None:
        g.add((node, SKOS.definition, Literal(description)))


def two_images():
    g = Graph()
    # stable blank-node ids: the fixture is built once per side
    _image(g, BNode("img1"), "Diagram for Cadastral Survey Dataset.", 0,
           "https://example.org/spec_files/CSD_logical.png",
           name="CSD logical", fmt="image/png", source="ICSM",
           description="The logical model.")
    _image(g, BNode("img2"), "Overview.", 1,
           "https://example.org/spec_files/overview.png")
    return ((EX.CSD, g), {})


def no_image():
    g = Graph()
    g.add((EX.CSD, RDF.type, SDO.Dataset))
    return ((EX.CSD, g), {})


VERDICT = run_pair(__file__, entry="get_images",
                   calls=[two_images, no_image])
