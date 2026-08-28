# Extracted from ruirzma/UPTO@6827ed41e5 : utils.py
# region: construct_UPTO_individual (lines 291-402, stratum add_in_loop)
# licence of the source repository: see meta.json
import rdflib
from rdflib import RDF, Namespace, URIRef, Literal, OWL ,XSD
names = Namespace("http://www.urbanpatchtopologyontology.org/upto#")
containsTile = URIRef(names["containsTile"])
containsStreet = URIRef(names["containsStreet"])
hasAvgBuildingHeight  = URIRef(names["hasAvgBuildingHeight"])
hasBuildingDensity = URIRef(names["hasBuildingDensity"])
hasVegetationDensity =  URIRef(names["hasVegetationDensity"])
hasVerticalToHorizontalRatio = URIRef(names["hasVerticalToHorizontalRatio"])
containsBuilding = URIRef(names["containsBuilding"])
containsVegetation = URIRef(names["containsVegetation"])
withinPatch = URIRef(names["withinPatch"])
hasTileNeighbor = URIRef(names["hasTileNeighbor"])
hasStreetNeighbor = URIRef(names["hasStreetNeighbor"])
withinTile = URIRef(names["withinTile"])

def construct_UPTO_individual(cityName, VG_gdf, building_gdf, street_gdf, urban_tile_gdf, urban_patch_gdf_prj):
    # Build graph
    graph = rdflib.Graph()
    graph.parse("init.ttl", format="turtle")

    ###################################################
    # Add UPTO individuals
    for j in range(len(VG_gdf)):
        Vegetation_Num = VG_gdf["osmscID"][j]
        add_Vegetation_Individual(graph,Vegetation_Num,VG_gdf )

    for z in range(len(building_gdf)):
        Building_Num = building_gdf["osmscID"][z]
        add_Building_Individual(graph,Building_Num, building_gdf)

    for q in range(len(street_gdf)):
        Street_Num = street_gdf["osmscID"][q]
        add_Street_Individual(graph, Street_Num, street_gdf)

    for k in range(len(urban_tile_gdf)):  
        UrbanTile_Num = urban_tile_gdf["osmscID"][k]
        add_UrbanTile_Individual(graph, UrbanTile_Num, urban_tile_gdf)

    for i in range(len(urban_patch_gdf_prj)):
        UrbanPatch_Num = urban_patch_gdf_prj["osmscID"][i]
        add_UrbanPatch_Individual(graph, UrbanPatch_Num, urban_patch_gdf_prj)


    # Add spatial semantics

    for k in range(len(urban_tile_gdf)):
        UrbanTile_Num = urban_tile_gdf["osmscID"][k]
        UrbanTile_Num_URI = URIRef(names[UrbanTile_Num])

        # withinTile for Building
        try:
            temp_1 = graph.objects(subject=UrbanTile_Num_URI,predicate = containsBuilding )
            bldg_URI_list = list(temp_1)
            for bldg_URI in bldg_URI_list:
                graph.add((bldg_URI, withinTile , UrbanTile_Num_URI)) 
        except:
            pass

        # withinTile for Vegetation
        try: 
            temp_2 = graph.objects(subject=UrbanTile_Num_URI,predicate = containsVegetation )
            VG_URI_list = list(temp_2)
            for VG_URI in VG_URI_list:
                graph.add((VG_URI, withinTile , UrbanTile_Num_URI))  
        except:
            pass

        # hasTileNeighbor for Street 
        try:
            temp_3 = graph.objects(subject=UrbanTile_Num_URI,predicate = hasStreetNeighbor )
            Street_URI_list = list(temp_3)
            for Street_URI in Street_URI_list:
                graph.add((Street_URI, hasTileNeighbor , UrbanTile_Num_URI))
        except:
            pass


    # hasTileNeighbor for UrbanTile
    condition = """
    SELECT ?UrbanTile_x ?UrbanTile_y
    WHERE { 
        ?UrbanTile_x :hasStreetNeighbor ?Street_z .
        ?UrbanTile_y :hasStreetNeighbor ?Street_z .
        FILTER (?UrbanTile_x != ?UrbanTile_y)
    }"""

    for row in graph.query(condition):
        graph.add((row.UrbanTile_x, hasTileNeighbor , row.UrbanTile_y)) 

    # withinPatch for UrbanTile Street 
    for i in range(len(urban_patch_gdf_prj)):

        UrbanPatch_Num = urban_patch_gdf_prj["osmscID"][i]
        UrbanPatch_Num_URI = URIRef(names[UrbanPatch_Num])

        # withinPatch for UrbanTile
        try:
            temp_1 = graph.objects(subject=UrbanPatch_Num_URI,predicate = containsTile )
            tile_URI_list = list(temp_1)
            for tile_URI in tile_URI_list:
                graph.add((tile_URI, withinPatch ,  UrbanPatch_Num_URI)) 
        except:
            pass

        # withinPatch for Street 
        try:
            temp_2 = graph.objects(subject=UrbanPatch_Num_URI,predicate = containsStreet )
            Street_URI_list = list(temp_2)
            for Street_URI in Street_URI_list:
                graph.add((Street_URI, withinPatch ,  UrbanPatch_Num_URI)) 
        except:
            pass

    # UWG_paras for UrbanPatch
    for i in range(len(urban_patch_gdf_prj)):

        UrbanPatch_Num = urban_patch_gdf_prj["osmscID"][i]
        UrbanPatch_Num_URI = URIRef(names[UrbanPatch_Num])

        AvgBuildingHeight, BuildingDensity, VegetationDensity, VerticalToHorizontalRatio = UWG_paras_for_UrbanPatch(graph, UrbanPatch_Num_URI)
        graph.add((UrbanPatch_Num_URI, hasAvgBuildingHeight ,  Literal(str(AvgBuildingHeight), datatype = XSD["decimal"]))) 
        graph.add((UrbanPatch_Num_URI, hasBuildingDensity ,  Literal(str(BuildingDensity), datatype = XSD["decimal"]))) 
        graph.add((UrbanPatch_Num_URI, hasVegetationDensity , Literal(str(VegetationDensity), datatype = XSD["decimal"]))) 
        graph.add((UrbanPatch_Num_URI, hasVerticalToHorizontalRatio ,  Literal(str( VerticalToHorizontalRatio), datatype = XSD["decimal"]))) 


    graph.serialize( cityName + ".ttl",format="turtle") 
