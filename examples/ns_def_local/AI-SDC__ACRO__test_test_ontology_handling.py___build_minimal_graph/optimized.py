# Extracted from AI-SDC/ACRO@eb1d6e370a : test/test_ontology_handling.py
# region: _build_minimal_graph (lines 21-55, stratum ns_def_local)
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

def _build_minimal_graph() -> rdflib.Graph:
    """Build a minimal RDF graph that satisfies ontology_handler expectations."""
    g = rdflib.Graph()
    p = rdflib.Namespace(PREFIX)
    for name, parent, definition in (
        ("LowCount", rdflib.URIRef("https://w3id.org/dpv/owl#Risk"), "Low count risk"),
        ("Frequencies", p.Statbarn, "Frequency statbarn"),
        ("FrequencyTable", p.Frequencies, "Frequency table analysis"),
        (
            "MinimumThresholdCheck",
            rdflib.URIRef("https://w3id.org/dpv/risk/owl#RiskEvaluation"),
            "Minimum threshold check def",
        ),
    ):
        g += [
            (p[name], rdflib.RDFS.subClassOf, parent),
            (p[name], rdflib.SKOS.definition, rdflib.Literal(definition)),
            (p[name], rdflib.SKOS.prefLabel, rdflib.Literal(name)),
        ]
    return g
