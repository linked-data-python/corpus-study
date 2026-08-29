# Extracted from leolani/cltl-dialogueevaluation@08f9bb88f6 : src/cltl/dialogue_evaluation/metrics/ontology_measures.py
# region: get_number_role_assertions (lines 158-164, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib

def get_number_role_assertions(graph: rdflib.Graph):
    """number of ABox Axioms: role assertions"""

    ra = len(
        graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x ?w ?y. ?w a owl:ObjectProperty}'))
    ans = ra
    return ans
