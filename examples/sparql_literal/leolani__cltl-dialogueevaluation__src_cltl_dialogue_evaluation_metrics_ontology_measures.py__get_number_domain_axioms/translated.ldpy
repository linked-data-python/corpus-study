# Extracted from leolani/cltl-dialogueevaluation@08f9bb88f6 : src/cltl/dialogue_evaluation/metrics/ontology_measures.py
# region: get_number_domain_axioms (lines 182-187, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib

def get_number_domain_axioms(graph: rdflib.Graph):
    """number of TBox Axioms: domain axioms """

    da = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x rdfs:domain ?y }'))
    ans = da
    return ans
