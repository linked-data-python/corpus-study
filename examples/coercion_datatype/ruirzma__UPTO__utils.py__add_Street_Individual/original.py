# Extracted from ruirzma/UPTO@6827ed41e5 : utils.py
# region: add_Street_Individual (lines 83-100, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import RDF, Namespace, URIRef, Literal, OWL ,XSD
from rdflib.namespace import OWL, RDF, RDFS
names = Namespace("http://www.urbanpatchtopologyontology.org/upto#")
Street = URIRef(names["Street"])
hasGeometry = URIRef(names["hasGeometry"])
hasArea = URIRef(names["hasArea"])
hasPerimeter = URIRef(names["hasPerimeter"])

def add_Street_Individual(graph, Street_Num, street_gdf):

    Street_Num_URI = URIRef(names[Street_Num])

    graph.add((Street_Num_URI, RDF.type, OWL.NamedIndividual))
    graph.add((Street_Num_URI, RDF.type, Street)) 

    graph.add((Street_Num_URI, hasArea , 
            Literal(list(street_gdf[street_gdf["osmscID"] == Street_Num].Street_area)[0], 
                    datatype = XSD["decimal"]))) 

    graph.add((Street_Num_URI, hasPerimeter , 
            Literal(list(street_gdf[street_gdf["osmscID"] == Street_Num].Street_perimeter)[0], 
                    datatype = XSD["decimal"]))) 

    # geometry
    geom_str = str(list(street_gdf[street_gdf["osmscID"] == Street_Num].geometry)[0])
    graph.add((Street_Num_URI, hasGeometry, Literal(geom_str, datatype = XSD["string"])))     
