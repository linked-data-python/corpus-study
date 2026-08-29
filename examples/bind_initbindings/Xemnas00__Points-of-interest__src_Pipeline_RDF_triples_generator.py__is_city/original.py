# Extracted from Xemnas00/Points-of-interest@39e9179949 : src/Pipeline/RDF_triples_generator.py
# region: is_city (lines 169-181, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF, RDFS, URIRef, Literal, XSD

def is_city(urificated_city):
    uri = URIRef('http://dbpedia.org/resource/' + urificated_city)
    pp = URIRef('http://dbpedia.org/ontology/PopulatedPlace')
    g_temp = Graph()
    g_temp.parse(uri)
    response = g_temp.query(
        "ASK {?uri a ?pp}",
        initBindings={'uri': uri, 'pp': pp}
    )

    print(str(uri) + " is a PopulatedPlace? " + str(response.askAnswer))

    return response.askAnswer
