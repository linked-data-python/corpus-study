# Extracted from interior-night/kglab-ggg@735ae3c49c : scripts/oxrdf.py
# region: run_query (lines 29-47, stratum sparql_literal)
# licence of the source repository: see meta.json
import time
QUDT_QUERY9 = """
PREFIX BASF_EC_RaMPO: <https://ontology.basf.net/ontology/BASF_EC_RaMPO/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT DISTINCT ?item WHERE { ?item rdfs:subClassOf ?item_class . FILTER(?item != owl:Nothing) . FILTER(?item != ?item_class) . FILTER(?item != BASF_EC_RaMPO:CoatingLayer) . FILTER(?interfaceClass != BASF_EC_RaMPO:CoatingLayer) . ?item rdfs:subClassOf ?restriction1 . ?restriction1 rdf:type owl:Restriction . ?restriction1 owl:onProperty BASF_EC_RaMPO:basedOn . ?restriction1 owl:onClass ?basedOn . { ?restriction1 owl:onClass ?basedOn . ?restriction1 owl:onClass ?base_layer . ?item rdfs:subClassOf ?restriction2 . ?restriction2 rdf:type owl:Restriction . ?restriction2 owl:onProperty BASF_EC_RaMPO:interactsWith . ?restriction2 owl:onClass ?interfaceClass } UNION { ?restriction1 owl:onClass ?basedOn . ?basedOn owl:unionOf/rdf:rest*/rdf:first ?base_layer . ?item rdfs:subClassOf ?restriction2 . ?restriction2 rdf:type owl:Restriction . ?restriction2 owl:onProperty BASF_EC_RaMPO:interactsWith . ?restriction2 owl:onClass ?interactsWith . ?interactsWith owl:unionOf/rdf:rest*/rdf:first ?interactsWithUnion . ?interactsWithUnion rdfs:subClassOf ?interfaceRestriction . ?interfaceRestriction rdf:type owl:Restriction . ?interfaceRestriction owl:onProperty BASF_EC_RaMPO:hasEquivalentCoatingLayer . ?interfaceRestriction owl:someValuesFrom ?interfaceClass . FILTER (?interfaceClass != ?base_layer) } OPTIONAL { ?item rdfs:label ?label } }
"""

def run_query (g) -> None:
    """measure the timing for a SPARQL query"""
    print(f"using graph: {g}")

    # query init
    init_time = time.time()
    query_iter = g.query(QUDT_QUERY9)

    duration = time.time() - init_time
    print(f"query init time: {duration:10.3f}")

    # query exec
    init_time = time.time()

    for row in query_iter:
        print(row.item)

    duration = time.time() - init_time
    print(f"query exec time: {duration:10.3f}", "\n")
