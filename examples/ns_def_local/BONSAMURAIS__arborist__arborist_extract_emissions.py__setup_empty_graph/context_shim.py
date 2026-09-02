# Context shim (see meta.json): subset of arborist/graph_common.py from
# BONSAMURAIS/arborist@da18f3d17c, so the region executes outside the
# package (the real file does `from .graph_common import add_common_elements`,
# a relative import that needs a real parent package to resolve, and
# `add_common_elements` itself reads `arborist.__version__` via
# `from . import __version__`).
#
# Copied verbatim (real IRIs, same triples, same use of `datetime.now()`),
# minus what `setup_empty_graph` never reaches: `generate_generic_graph`,
# `write_graph`, `Path`. `__version__` is inlined as the literal it resolves
# to in arborist/__init__.py (`VERSION = (0, 5)`).
#
# One compatibility fix, unrelated to the region under study: the source
# imports `DC` from `rdflib.namespace`, which on rdflib 7.2.1 (pinned, see
# README) is a `DefinedNamespace` restricted to the 15 Dublin Core Elements
# terms and raises on `DC.modified` (a DCTERMS term, not a DC Elements one) --
# the repository plainly ran against an rdflib where this was not enforced.
# Declaring `DC` as a plain `Namespace` on the same IRI reproduces that
# unrestricted behaviour and yields the identical URIRef for every `DC.x`
# this function uses; it changes no triple.
#
# Identical for both representations.
import datetime

from rdflib import Literal, RDF, URIRef, Namespace
from rdflib.namespace import OWL, FOAF, XSD, SKOS

DC = Namespace("http://purl.org/dc/elements/1.1/")

__version__ = "0.5"


class CommonNamespaces:
    def __init__(self):
        self.nb = Namespace("http://ontology.bonsai.uno/core#")
        self.owltime = Namespace("https://www.w3.org/TR/owl-time/")
        self.vann = Namespace("http://purl.org/vocab/vann/")
        self.dt = Namespace("http://purl.org/dc/dcmitype/")
        self.prov = Namespace("http://www.w3.org/ns/prov#")


NS = CommonNamespaces()


def add_common_elements(graph, base_uri, title, description, author):
    """Add common graph binds and a Dataset element (verbatim from graph_common.py)."""
    if base_uri.endswith("#") or base_uri.endswith("/"):
        raise ValueError("`base_uri` cannot end with '/' or '#'")

    prov = Namespace("http://www.w3.org/ns/prov#")
    bfoaf = Namespace("http://rdf.bonsai.uno/foaf/bonsai#")
    bprov = Namespace("http://rdf.bonsai.uno/prov/exiobase3_3_17#")

    graph.bind("bont", "http://ontology.bonsai.uno/core#")
    graph.bind("dc", DC)
    graph.bind("foaf", FOAF)
    graph.bind("xsd", XSD)
    graph.bind("owl", OWL)
    graph.bind("skos", SKOS)
    graph.bind("ot", "https://www.w3.org/TR/owl-time/")
    graph.bind("dtype", "http://purl.org/dc/dcmitype/")
    graph.bind("prov", prov)
    graph.bind("bprov", bprov)
    graph.bind("bfoaf", bfoaf)

    node = URIRef(base_uri)
    graph.add((node, RDF.type, NS.dt.Dataset))
    graph.add((node, DC.title, Literal(title)))
    graph.add((node, DC.description, Literal(description)))
    graph.add((node, FOAF.homepage, URIRef("{}documentation.html".format(base_uri))))
    graph.add((node, NS.vann.preferredNamespaceUri, URIRef("{}#".format(base_uri))))
    graph.add((node, OWL.versionInfo, Literal(__version__)))
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    graph.add((node, DC.modified, Literal(today, datatype=XSD.date)))
    graph.add((node, DC.publisher, bfoaf.bonsai))
    graph.add((node, DC.creator, bfoaf.bonsai))

    graph.add((node, RDF.type, prov.Collection))
    graph.add((node, prov.wasAttributedTo, bfoaf.bonsai))
    graph.add((node, prov.wasGeneratedBy, bprov["dataExtractionActivity_{}".format(__version__.replace(".", "_"))]))
    graph.add((node, prov.generatedAtTime, Literal(today, datatype=XSD.date)))
    graph.add(
        (
            node,
            URIRef("http://creativecommons.org/ns#license"),
            URIRef("http://creativecommons.org/licenses/by/3.0/"),
        )
    )

    return graph
