# Extracted from AI-SDC/ACRO@eb1d6e370a : test/test_ontology_handling.py
# region: _build_minimal_graph (lines 21-55, stratum ns_def_local)
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

def _build_minimal_graph() -> rdflib.Graph:
    """Build a minimal RDF graph that satisfies ontology_handler expectations."""
    g = rdflib.Graph()
    p = rdflib.Namespace(PREFIX)
    skos = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")
    rdfs = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
    dpv_owl = rdflib.Namespace("https://w3id.org/dpv/owl#")

    risk_uri = p.LowCount
    g.add((risk_uri, rdfs.subClassOf, dpv_owl.Risk))
    g.add((risk_uri, skos.definition, rdflib.Literal("Low count risk")))
    g.add((risk_uri, skos.prefLabel, rdflib.Literal("LowCount")))

    barn_uri = p.Frequencies
    g.add((barn_uri, rdfs.subClassOf, p.Statbarn))
    g.add((barn_uri, skos.definition, rdflib.Literal("Frequency statbarn")))
    g.add((barn_uri, skos.prefLabel, rdflib.Literal("Frequencies")))

    analysis_uri = p.FrequencyTable
    g.add((analysis_uri, rdfs.subClassOf, barn_uri))
    g.add((analysis_uri, skos.definition, rdflib.Literal("Frequency table analysis")))
    g.add((analysis_uri, skos.prefLabel, rdflib.Literal("FrequencyTable")))

    check_uri = p.MinimumThresholdCheck
    g.add(
        (
            check_uri,
            rdfs.subClassOf,
            rdflib.URIRef("https://w3id.org/dpv/risk/owl#RiskEvaluation"),
        )
    )
    g.add((check_uri, skos.definition, rdflib.Literal("Minimum threshold check def")))
    g.add((check_uri, skos.prefLabel, rdflib.Literal("MinimumThresholdCheck")))

    return g
