"""Validation driver for stevereiner__flexible-graphrag__flexible-graphrag_rdf_ontology_manager.py__OntologyManager_get_xsd_type_map.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a method (``self.graph``, ``self.entities``, ``self.relations``,
``self._uri_to_name``); the fixture is a tiny stand-in ``self`` built here
(reading-oracle style, but the "input" is an object rather than a Turtle
file, so it is constructed directly instead of via ``fixture=``).

Repair 2026-10-31 (mutation audit):

  - ``_uri_to_name`` is now the repository's own body
    (ontology_manager.py:306-313), not an approximation.
  - the graph gains ``ex:ns#`` (a DatatypeProperty whose local name is
    empty: ``_uri_to_name`` gives "", the region's ``if name:`` drops it)
    and ``ex:emptyRange`` (``rdfs:range ""``: the region's ``if row.range``
    treats the falsy literal as absent and falls back to xsd:string). Each
    kills a mutant that stayed green: ``if name`` forced to True, and
    ``if row.range`` read as ``is not None``.
  - a second call with ``self.graph = None``, the repository's own initial
    state (``self.graph: Optional[Graph] = None``, line 68, until an
    ontology is loaded): the region skips the query and keeps only the
    entity/relation fallback. It kills the mutant forcing
    ``if self.graph is not None`` to True (s{ }(None) raises).
"""
from types import SimpleNamespace

from rdflib import Graph, Namespace, RDF, RDFS, URIRef
from rdflib import Literal as RdfLiteral

from rdfeval.harness import run_pair

OWL = Namespace("http://www.w3.org/2002/07/owl#")
EX = Namespace("http://example.org/")


def _uri_to_name(uri):
    # verbatim body of OntologyManager._uri_to_name (ontology_manager.py:306)
    if uri is None:
        return None
    uri_str = str(uri)
    # Extract local name from URI (after # or /)
    name = uri_str.split('#')[-1].split('/')[-1]
    return name.upper()


def _make_self(with_graph=True):
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
    # Datatype property with an empty local name: `if name:` must drop it.
    graph.add((URIRef("http://example.org/ns#"), RDF.type, OWL.DatatypeProperty))
    graph.add((URIRef("http://example.org/ns#"), RDFS.range, EX.Ignored))
    # Falsy range literal: `if row.range` falls back to xsd:string.
    graph.add((EX.emptyRange, RDF.type, OWL.DatatypeProperty))
    graph.add((EX.emptyRange, RDFS.range, RdfLiteral("")))

    # "age" is a fallback-only key (int -> xsd:integer); "salary" is already
    # set by the query above, so the fallback must NOT override it; "note"
    # has a Python type the _PY_TO_XSD table does not know, so it must fall
    # back to xsd:string via the dict's default.
    entity = SimpleNamespace(properties={"age": "int", "salary": "string", "note": "custom"})
    relation = SimpleNamespace(properties={"assignment_percentage": "float"})
    return SimpleNamespace(
        graph=graph if with_graph else None,
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
    calls=[lambda: ((_make_self(),), {}),
           lambda: ((_make_self(with_graph=False),), {})],
)
