"""Validation driver for stevereiner__flexible-graphrag__flexible-graphrag_rdf_ontology_manager.py__OntologyManager_get_xsd_type_map.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a method (``self.graph``, ``self.entities``, ``self.relations``,
``self._uri_to_name``); the fixture is a tiny stand-in ``self`` built here
(reading-oracle style, but the "input" is an object rather than a Turtle
file, so it is constructed directly instead of via ``fixture=``).
"""
from types import SimpleNamespace

from rdflib import Graph, Namespace, RDF, RDFS

from rdfeval.harness import run_pair

OWL = Namespace("http://www.w3.org/2002/07/owl#")
EX = Namespace("http://example.org/")


def _uri_to_name(uri):
    return str(uri).rsplit("#", 1)[-1].rsplit("/", 1)[-1].upper()


def _make_self():
    # A fixed identifier so the two SimpleNamespace fixtures — one built per
    # side, per the harness's "fresh mutable argument" contract — compare
    # equal on the input side; the function only reads this graph.
    graph = Graph(identifier=EX.fixtureGraph)
    graph.bind("owl", OWL)
    graph.bind("rdfs", RDFS)
    graph.bind("ex", EX)
    # Datatype property with an explicit rdfs:range.
    graph.add((EX.salary, RDF.type, OWL.DatatypeProperty))
    graph.add((EX.salary, RDFS.range, Namespace("http://www.w3.org/2001/XMLSchema#")["decimal"]))
    # Datatype property with no rdfs:range -> falls back to xsd:string.
    graph.add((EX.nickname, RDF.type, OWL.DatatypeProperty))
    # Neighbourhood that must NOT match: an object property, not a datatype one.
    graph.add((EX.worksFor, RDF.type, OWL.ObjectProperty))
    graph.add((EX.worksFor, RDFS.range, EX.Organization))

    # "age" is a fallback-only key (int -> xsd:integer); "salary" is already
    # set by the query above, so the fallback must NOT override it; "note"
    # has a Python type the _PY_TO_XSD table does not know, so it must fall
    # back to xsd:string via the dict's default.
    entity = SimpleNamespace(properties={"age": "int", "salary": "string", "note": "custom"})
    relation = SimpleNamespace(properties={"assignment_percentage": "float"})
    return SimpleNamespace(
        graph=graph,
        entities={"Person": entity},
        relations={"Assignment": relation},
        _uri_to_name=_uri_to_name,
    )


# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='get_xsd_type_map',
    calls=[lambda: ((_make_self(),), {})],
)
