# Extracted from ruirzma/UPTO@6827ed41e5 : utils.py
# region: add_Building_Individual (lines 103-128, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import RDF, Namespace, URIRef, Literal, OWL ,XSD
from rdflib.namespace import OWL, RDF, RDFS
names = Namespace("http://www.urbanpatchtopologyontology.org/upto#")
Building = URIRef(names["Building"])
hasGeometry = URIRef(names["hasGeometry"])
hasArea = URIRef(names["hasArea"])
hasPerimeter = URIRef(names["hasPerimeter"])
hasHeight = URIRef(names["hasHeight"])
hasBuildingType = URIRef(names["hasBuildingType"])

def add_Building_Individual(graph, Building_Num, building_gdf):

    Building_Num_URI = URIRef(names[Building_Num])

    graph.add((Building_Num_URI, RDF.type, OWL.NamedIndividual))
    graph.add((Building_Num_URI, RDF.type, Building)) 

    graph.add((Building_Num_URI, hasArea , 
            Literal(list(building_gdf[building_gdf["osmscID"] == Building_Num].Building_area)[0], 
                    datatype = XSD["decimal"]))) 

    graph.add((Building_Num_URI, hasPerimeter , 
            Literal(list(building_gdf[building_gdf["osmscID"] == Building_Num].Building_perimeter)[0], 
                    datatype = XSD["decimal"]))) 

    graph.add((Building_Num_URI, hasBuildingType , 
            Literal("Office", 
                    datatype = XSD["string"]))) 

    graph.add((Building_Num_URI, hasHeight , 
            Literal(list(building_gdf[building_gdf["osmscID"] == Building_Num].Building_height)[0], 
                    datatype = XSD["decimal"]))) 

    # geometry
    geom_str = str(list(building_gdf[building_gdf["osmscID"] == Building_Num].geometry)[0])
    graph.add((Building_Num_URI, hasGeometry, Literal(geom_str, datatype = XSD["string"]))) 
