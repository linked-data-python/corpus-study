"""Validation driver: get_text_object reads an sdo:TextObject description.

The region is a pure reader — it only *looks up* terms — so the fixtures
supply the graph and the harness compares the returned TextObject (a
dataclass, hence value equality) as well as the untouched input graph.
"""
from rdflib import DCTERMS, SDO, SH, Graph, Literal, URIRef

from rdfeval.harness import run_pair

EXAMPLE = URIRef("https://example.com/example/1")

FULL = """
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix sdo: <https://schema.org/> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://example.com/example/1> a sdo:TextObject ;
    sdo:name "A Turtle example" ;
    sdo:description "How to state an address" ;
    sdo:encodingFormat "text/turtle" ;
    dcterms:source <https://example.com/spec> ;
    sh:order 2 ;
    sdo:text \"\"\"
        ex:addr a ex:Address ;
            ex:street "1 Main St" .
    \"\"\" .
"""

MINIMAL = """
@prefix sdo: <https://schema.org/> .

<https://example.com/example/1> a sdo:TextObject ;
    sdo:text "ex:addr a ex:Address ." .
"""


def _graph(data):
    g = Graph()
    g.parse(data=data, format="turtle")
    return g


def full_example():
    return ((EXAMPLE, _graph(FULL)), {})


def minimal_example():
    return ((EXAMPLE, _graph(MINIMAL)), {})


VERDICT = run_pair(__file__, entry="get_text_object",
                   calls=[full_example, minimal_example])
