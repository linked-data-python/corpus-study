# Extracted from TDCC-NES/askwol@3534557e8b : tests/test_term_inventory.py
# region: test_own_namespace_that_is_a_wellknown_vocab_is_internal (lines 128-142, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import OWL, RDF, RDFS, XSD
from askwol.models import Status
from askwol.term_inventory import (
    check_datatypes,
    check_domains_ranges,
    check_term_inventory,
)

def test_own_namespace_that_is_a_wellknown_vocab_is_internal():
    # Validating a well-known vocabulary (here FOAF) must treat its own terms as
    # internal, even though FOAF is in askwol's external allowlist.
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    g = Graph()
    g.add((FOAF[""], RDF.type, OWL.Ontology))
    g.add((FOAF["Person"], RDF.type, OWL.Class))
    g.add((FOAF["knows"], RDF.type, OWL.ObjectProperty))

    report = check_term_inventory(g)

    assert report.status == Status.OK
    assert report.total_terms == 2
    names = {e.display_name for e in report.entries}
    assert {"Person", "knows"} <= names
