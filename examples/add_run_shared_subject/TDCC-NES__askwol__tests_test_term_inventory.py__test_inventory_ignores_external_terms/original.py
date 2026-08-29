# Extracted from TDCC-NES/askwol@3534557e8b : tests/test_term_inventory.py
# region: test_inventory_ignores_external_terms (lines 112-119, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, RDF, RDFS, XSD
from askwol.term_inventory import (
    check_datatypes,
    check_domains_ranges,
    check_term_inventory,
)
EX = Namespace("https://example.org/ont#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

def test_inventory_ignores_external_terms():
    g = _base_graph()
    g.add((EX["Person"], RDF.type, OWL.Class))
    g.add((EX["Person"], RDFS.subClassOf, FOAF["Agent"]))

    report = check_term_inventory(g)

    assert all("foaf" not in e.term for e in report.entries)
