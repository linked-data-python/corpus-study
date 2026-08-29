# Extracted from leolani/cltl-dialogueevaluation@08f9bb88f6 : src/cltl/dialogue_evaluation/metrics/ontology_measures.py
# region: get_number_GCI (lines 167-179, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib

def get_number_GCI(graph: rdflib.Graph, mat=None):
    """number of TBox Axioms: general concept inclusions"""

    sco = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x rdfs:subClassOf ?y }'))
    dis = len(graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x owl:disjointWith ?y }'))
    ans = sco + dis

    if mat == None or not mat:
        eq = 2 * len(
            graph.query('PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT * WHERE { ?x owl:equivalentClass ?y }'))
        ans = sco + eq

    return ans
