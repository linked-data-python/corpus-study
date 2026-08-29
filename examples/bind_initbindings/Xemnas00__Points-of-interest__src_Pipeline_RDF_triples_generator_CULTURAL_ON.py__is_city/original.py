# Extracted from Xemnas00/Points-of-interest@39e9179949 : src/Pipeline/RDF_triples_generator_CULTURAL_ON.py
# region: is_city (lines 131-145, stratum bind_initbindings)
# licence of the source repository: see meta.json
from urllib.error import HTTPError
from rdflib import Graph, RDF, RDFS, URIRef, Literal, XSD

def is_city(urificated_city):
    uri = URIRef('http://dbpedia.org/resource/' + urificated_city)
    pp = URIRef('http://dbpedia.org/ontology/PopulatedPlace')
    g_temp = Graph()
    g_temp.parse(uri)
    try:
        response = g_temp.query(
            "ASK {?uri a ?pp}",
            initBindings={'uri': uri, 'pp': pp}
        )
    except HTTPError:
        return False
    print(str(uri) + " is a PopulatedPlace? " + str(response.askAnswer))

    return response.askAnswer
