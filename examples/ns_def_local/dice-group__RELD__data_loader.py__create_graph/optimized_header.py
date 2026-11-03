# Extracted from dice-group/RELD@7ca93acbb6 : data_loader.py
# region: create_graph (lines 789-819, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph

def create_graph():
    g = Graph()
    #datasetURI = Namespace("https://reld.dice-research.org/")
    for prefix, namespace in [
        ("reld", "http://reld.dice-research.org/schema/"),
        ("reldr", "http://reld.dice-research.org/resource/"),
        ("dcterms", "http://purl.org/dc/terms/"),
        ("dbo", "http://dbpedia.org/ontology/"),
        ("ps", "http://www.wikidata.org/prop/statement/"),
        ("freebase", "http://rdf.freebase.com/ns"),
        ("owl", "http://www.w3.org/2002/07/owl#"),
        ("dbo", "http://dbpedia.org/property/"),
        ("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        ("prov", "http://www.w3.org/ns/prov#"),
        ("dc", "http://purl.org/dc/elements/1.1/"),
        ("nif", "http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#"),
    ]:
        g.bind(prefix, namespace)
    return g
