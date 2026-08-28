"""Validation driver: get_domain_includes reads sdo:domainIncludes.

The region is a pure reader, so the fixtures supply the graph and the
dataset and the harness compares the returned list of model Class objects
plus the untouched inputs.
"""
from rdflib import Dataset, Graph, URIRef

from rdfeval.harness import run_pair

PROP = URIRef("https://example.com/prop/hasAddress")

DATA = """
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sdo: <https://schema.org/> .

<https://example.com/prop/hasAddress> a sdo:Property ;
    sdo:domainIncludes <https://example.com/class/Person> ,
                       <https://example.com/class/Organisation> .

<https://example.com/class/Person> rdfs:label "Person" .
<https://example.com/class/Organisation> rdfs:label "Organisation" .
<https://example.com/class/Employee> rdfs:subClassOf
    <https://example.com/class/Person> ;
    rdfs:label "Employee" .
"""

NO_DOMAIN = """
@prefix sdo: <https://schema.org/> .

<https://example.com/prop/hasAddress> a sdo:Property .
"""


def _inputs(data):
    g = Graph()
    g.parse(data=data, format="turtle")
    # `db` is only consulted by get_name as a fallback when the profile
    # graph carries no label; it is passed as None here because the harness
    # compares every rdflib Graph argument by isomorphism and a Dataset
    # yields quads, which rdflib.compare cannot ingest.  The region itself
    # never touches `db` — it forwards it to get_class.
    return ((PROP, g, None), {})


def two_domains():
    return _inputs(DATA)


def no_domain():
    return _inputs(NO_DOMAIN)


VERDICT = run_pair(__file__, entry="get_domain_includes",
                   calls=[two_domains, no_domain])
