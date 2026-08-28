"""Validation driver for RDFLib__pyLODE__…__get_root_profile_iri.

A module-level function taking a Graph.  Only the two returning branches can
be exercised: the harness aborts on any exception, so the two ValueError
branches (more than one profile, no profile and no single ontology) cannot be
covered here — they raise identically on both sides by construction, the
message strings being untouched Python f-strings.
"""
from rdflib import Graph, URIRef

from rdfeval.harness import run_pair

ONE_PROFILE = """
@prefix prof: <http://www.w3.org/ns/dx/prof/> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix ex:   <http://example.com/> .

ex:profile a prof:Profile .
ex:onto    a owl:Ontology .
"""

ONLY_ONTOLOGY = """
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix ex:  <http://example.com/> .

ex:onto a owl:Ontology .
"""


def _graph(ttl):
    g = Graph(identifier=URIRef("http://example.com/g"))
    g.parse(data=ttl, format="turtle")
    return ((g,), {})


VERDICT = run_pair(__file__, entry="get_root_profile_iri",
                   calls=[lambda: _graph(ONE_PROFILE),
                          lambda: _graph(ONLY_ONTOLOGY)])
