# Extracted from city-knowledge-graphs/python-2024@81a87ded33 : lab4/queryLocalRDFGraph_Playground.py
# region: queryLocalGraph (lines 8-48, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph

def queryLocalGraph():

    #Example from  https://www.stardog.com/tutorials/data-model/

    #Loads KG
    g = Graph()
    g.parse("./data/playground.ttl", format="ttl")


    print("Loaded '" + str(len(g)) + "' triples.")

    #for s, p, o in g:
    #    print((s.n3(), p.n3(), o.n3()))


    print("Females:")

    qres = g.query(
    """SELECT ?thing ?name where {
      ?thing tto:sex "female" .
      ?thing dbp:name ?name .
    }""")


    for row in qres:
        #Row is a list of matched RDF terms: URIs, literals or blank nodes
        print("%s is female with name '%s'" % (str(row.thing),str(row.name)))



    #Same but with loading a query from a file
    print("Females (query from file):")
    query_file = "./data/query.txt"
    query = open(query_file, 'r').read()

    qres = g.query(query)


    for row in qres:
        #Row is a list of matched RDF terms: URIs, literals or blank nodes
        print("%s is female with name '%s'" % (str(row.thing),str(row.name)))
