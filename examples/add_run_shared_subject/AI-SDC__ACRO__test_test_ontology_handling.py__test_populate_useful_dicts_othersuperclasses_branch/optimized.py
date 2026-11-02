# Extracted from AI-SDC/ACRO@eb1d6e370a : test/test_ontology_handling.py
# region: test_populate_useful_dicts_othersuperclasses_branch (lines 216-237, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import rdflib
from context_shim import (  # context shim -- see meta.json
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
    subject = rdflib.URIRef(PREFIX + "TestClass")
    g += [(subject, rdflib.SKOS.definition, rdflib.Literal("a test class")),
          (subject, rdflib.SKOS.prefLabel, rdflib.Literal("Test Class")),
          (subject, rdflib.RDFS.subClassOf, rdflib.URIRef("http://example.com/parent1")),
          (subject, rdflib.RDFS.subClassOf, rdflib.URIRef("http://example.com/parent2"))]

    _, _, othersuperclasses = populate_useful_dicts(g)

    assert "TestClass" in othersuperclasses
    # Both parents should be present
    assert len(othersuperclasses["TestClass"]) >= 2


# Demo harness (identical on both sides, see meta.json): the test function
# builds its graph as a local variable and never returns or exposes it, so
# a plain call has nothing for run_pair to observe (no return value, no
# argument, no stdout). context_shim's populate_useful_dicts records the
# graph it receives in LAST_GRAPH; this harness calls the (untouched) test
# function -- which still raises if either side's own downstream assertions
# fail -- then hands back that captured graph for isomorphism comparison,
# the region's oracle.
import context_shim


def demo():
    test_populate_useful_dicts_othersuperclasses_branch()
    return context_shim.LAST_GRAPH
