"""Validation driver for RDFLib__pyLODE__pylode_profiles_supermodel_query___init__.py__get_examples.

`get_examples` is a pure read: it collects the sdo:workExample objects of a
subject and turns each into a TextObject or an ImageObject.  The fixtures use
the shape documented in the source file's own `get_images` docstring (a
container class with schema.org example nodes).  The returned dataclasses come
from the shared shim module, so they compare by value across the two runs.
"""
import sys

sys.dont_write_bytecode = True  # the shim next to this driver is imported

from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

CONTAINER = URIRef("https://example.com/container/CSD")

DATA = """
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix schema: <https://schema.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix container: <https://example.com/container/> .

container:CSD
  schema:workExample [
    a schema:ImageObject ;
    schema:name "CSD diagram" ;
    schema:caption "Diagram for Cadastral Survey Dataset." ;
    schema:contentUrl "https://example.com/CSD_logical.png"^^xsd:anyURI ;
    schema:encodingFormat "image/png" ;
    dcterms:source "https://example.com/spec" ;
    sh:order 1 ;
  ] ,
  [
    a schema:TextObject ;
    schema:name "CSD in Turtle" ;
    schema:description "A minimal instance." ;
    schema:encodingFormat "text/turtle" ;
    sh:order 0 ;
    schema:text \"\"\"
        container:x a schema:Thing .
    \"\"\" ;
  ] .

container:Empty a schema:Thing .
"""


def _graph():
    g = Graph()
    g.parse(data=DATA, format="turtle")
    return g


def two_examples():
    return ((CONTAINER, _graph()), {})


def no_examples():
    return ((URIRef("https://example.com/container/Empty"), _graph()), {})


VERDICT = run_pair(__file__, entry="get_examples",
                   calls=[two_examples, no_examples])
