# Extracted from city-knowledge-graphs/python@aa759f7438 : lab2/createTriples.py
# region: createTriples (lines 15-58, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
from rdflib.namespace import OWL, RDF, RDFS, FOAF, XSD

def createTriples():

    #Empty graph
    g = Graph()

    #Special namspaces to create  
    city = Namespace("http://www.example.org/university/london/city#")
    dbpo = Namespace("https://dbpedia.org/ontology/")

    #Prefixes
    g.bind("foaf", FOAF) #FOAF is given as defaulty namespace
    g.bind("city", city) #city is a newly created namespace
    g.bind("dbpo", dbpo) #dbpo is a newly created namespace 

    #These lines are equivalent:    
    #ernesto = URIRef("http://www.example.org/university/london/city#ernesto")
    #city.ernesto

    #print(city.ernesto)

    bnode = BNode()  # a GUID is generated

    name = Literal('Ernesto Jimenez-Ruiz', datatype=XSD.string)  # lang="en" for language tags
    year = Literal('2021', datatype=XSD.gYear)  # lang="en" for language tags


    g.add((city.inm713, RDF.type, city.Module))
    g.add((city.ernesto, RDF.type, FOAF.Person))
    g.add((city.ernesto, FOAF.name, name))
    g.add((city.ernesto, city.teaches, city.inm713))

    g.add((bnode, RDF.type, RDF.Statement ))
    g.add((bnode, RDF.subject, city.ernesto ))
    g.add((bnode, RDF.predicate, city.teaches ))
    g.add((bnode, RDF.object, city.inm713 ))
    g.add((bnode, dbpo.year, year ))




    print("Saving graph to 'lab2_task5.1_rdflib.ttl':")

    print(g.serialize(format="turtle").decode("utf-8"))    
    g.serialize(destination='lab2_task5.1_rdflib.ttl', format='ttl')
