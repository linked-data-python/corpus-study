# Extracted from city-knowledge-graphs/python-2024@81a87ded33 : lab2/createTriples.py
# region: createTriples (lines 15-61, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import BNode, FOAF, Graph, Literal, Namespace, RDF, RDFS, XSD

def createTriples():

    #Empty graph
    g = Graph()

    #Special namspaces to create  
    city = Namespace("http://www.example.org/university/london/city#")
    dbpo = Namespace("http://dbpedia.org/ontology/")

    #Prefixes
    g.bind("foaf", FOAF) #FOAF is given as defaulty namespace
    g.bind("city", city) #city is a newly created namespace
    g.bind("dbpo", dbpo) #dbpo is a newly created namespace 

    #These lines are equivalent:    
    #ernesto = URIRef("http://www.example.org/university/london/city#ernesto")
    #city.ernesto

    #print(city.ernesto)

    bnode = BNode()  # a GUID is generated

    g += [(city.inm713, RDF.type, city.Module),
          (city.ernesto, RDF.type, city.Lecturer),
          (city.Lecturer, RDFS.subClassOf, FOAF.Person),
          # lang="en" for language tags
          (city.ernesto, FOAF.name, Literal('Ernesto Jimenez-Ruiz', datatype=XSD.string)),
          (city.ernesto, city.teaches, city.inm713),
          (bnode, RDF.type, RDF.Statement),
          (bnode, RDF.subject, city.ernesto),
          (bnode, RDF.predicate, city.teaches),
          (bnode, RDF.object, city.inm713),
          (bnode, dbpo.year, Literal('2024', datatype=XSD.gYear))]

    print("Saving graph to 'lab2_example_rdflib.ttl':")

    print(g.serialize(format="turtle"))    
    g.serialize(destination='./data/lab2_example_rdflib.ttl', format='ttl')
