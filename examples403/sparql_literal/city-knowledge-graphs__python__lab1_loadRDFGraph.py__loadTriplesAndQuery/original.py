# Extracted from city-knowledge-graphs/python@aa759f7438 : lab1/loadRDFGraph.py
# region: loadTriplesAndQuery (lines 10-37, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph

def loadTriplesAndQuery():

    #Example from  https://www.stardog.com/tutorials/data-model/

    g = Graph()
    g.parse("beatles.ttl", format="ttl")


    print("Printing '" + str(len(g)) + "' triples.")


    #for stmt in g:    
        #print(stmt)

    for s, p, o in g:
        print((s.n3(), p.n3(), o.n3()))


    print("\nSolo artists:")

    qres = g.query(
    """SELECT DISTINCT ?x
       WHERE {
          ?x rdf:type <http://stardog.com/tutorial/SoloArtist> .
       }""")

    for row in qres:
        print("%s is a SoloArtist " % row)
