# Extracted from leolani/cltl-dialogueevaluation@08f9bb88f6 : src/cltl/dialogue_evaluation/metrics/brain_measures.py
# region: get_number_triples (lines 4-7, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib

def get_number_triples(graph: rdflib.Graph):
    ans = graph.query('SELECT (COUNT(*) as ?triples) WHERE {?s ?p ?o .}')
    ans = [row for row in ans]
    return float(ans[0].triples)
