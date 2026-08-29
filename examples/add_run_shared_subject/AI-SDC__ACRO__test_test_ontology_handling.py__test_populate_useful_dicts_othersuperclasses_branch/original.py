# Extracted from AI-SDC/ACRO@eb1d6e370a : test/test_ontology_handling.py
# region: test_populate_useful_dicts_othersuperclasses_branch (lines 216-237, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import rdflib
from acro.ontology_handler import (
    PREFIX,
    is_uri,
    make_ischeckedby,
    make_ismitigatedby,
    make_save_analyses,
    make_save_risks,
    make_save_statbarns,
    populate_useful_dicts,
    print_nested_dict,
)

def test_populate_useful_dicts_othersuperclasses_branch() -> None:
    """Populate_useful_dicts() appends to existing list when key already in othersuperclasses."""
    g = rdflib.Graph()
    subclass_ref = rdflib.URIRef("http://www.w3.org/2000/01/rdf-schema#subClassOf")
    definition_ref = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#definition")
    preflabel_ref = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#prefLabel")

    subject = rdflib.URIRef(PREFIX + "TestClass")
    g.add((subject, definition_ref, rdflib.Literal("a test class")))
    g.add((subject, preflabel_ref, rdflib.Literal("Test Class")))

    parent1 = rdflib.URIRef("http://example.com/parent1")
    parent2 = rdflib.URIRef("http://example.com/parent2")
    g.add((subject, subclass_ref, parent1))
    g.add((subject, subclass_ref, parent2))

    _, _, othersuperclasses = populate_useful_dicts(g)

    key = "TestClass"
    assert key in othersuperclasses
    # Both parents should be present
    assert len(othersuperclasses[key]) >= 2
