# Extracted from dice-group/RELD@7ca93acbb6 : data_loader.py
# region: create_graph (lines 789-819, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, Namespace # here is some error

def create_graph():
    g = Graph()
    prop = Namespace("http://reld.dice-research.org/schema/")
    res = Namespace("http://reld.dice-research.org/resource/")
    #datasetURI = Namespace("https://reld.dice-research.org/")
    dbo = Namespace("http://dbpedia.org/ontology/")
    freebase = Namespace("http://rdf.freebase.com/ns")
    wikidata = Namespace("http://www.wikidata.org/prop/statement/")
    owl = Namespace("http://www.w3.org/2002/07/owl#")
    dc = Namespace("http://purl.org/dc/elements/1.1/")
    dcterms = Namespace("http://purl.org/dc/terms/")
    nif = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
    prov = Namespace("http://www.w3.org/ns/prov#")
    dbpedia = Namespace("http://dbpedia.org/property/")
    rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    g.bind("reld", prop)
    g.bind("reldr", res)
    g.bind("dcterms",dcterms)
    g.bind("dbo",dbo)
    g.bind("ps",wikidata)
    g.bind('freebase',freebase)
    g.bind('owl',owl)
    g.bind('dbo',dbpedia)
    g.bind('rdf',rdf)
    g.bind('prov',prov)
    g.bind('dc',dc)
    g.bind('nif',nif)


    return g
