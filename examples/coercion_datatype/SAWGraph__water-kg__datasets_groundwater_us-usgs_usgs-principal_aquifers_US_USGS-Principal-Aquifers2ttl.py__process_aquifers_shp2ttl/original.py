# Extracted from SAWGraph/water-kg@032ec41357 : datasets/groundwater/us-usgs/usgs-principal_aquifers/US_USGS-Principal-Aquifers2ttl.py
# region: process_aquifers_shp2ttl (lines 124-161, stratum coercion_datatype)
# licence of the source repository: see meta.json
import geopandas as gpd
from rdflib import Graph, Literal
from rdflib.namespace import GEO, OWL, PROV, RDF, RDFS, SDO, XSD
from namespaces import _PREFIX
logger = logging.getLogger(__name__)

def process_aquifers_shp2ttl(infile, outfile):
    """Triplifies the principal aquifer data in a .shp file and saves the result as a .ttl file

    :param infile: a .shp file with NHD water body data
    :param outfile: the path and name for the .ttl file
    :return:
    """
    logger.info(f'Load principal aquifer shapefile from {infile}')

    # Read principall aquifers to a GeoDataframe
    gdf_aquifers = gpd.read_file(infile)

    logger.info('Intialize RDFLib Graph')
    kg = initial_kg(_PREFIX)  # Create an empty Graph() with SAWGraph namespaces
    count = 1  # For processing updates printed to terminal
    n = len(gdf_aquifers.index)  # For processing updates printed to terminal
    logger.info(f'Triplify principal aquifers')
    for row in gdf_aquifers.itertuples():
        # Get IRIs for the current principal aquifer and its geometry
        aqiri, geomiri = build_iris(row.OBJECTID_1, _PREFIX)
        kg.add((aqiri, RDF.type, _PREFIX['gwml2']['GW_Aquifer']))

        # Triplify the geometry for the current principal aquifer
        kg.add((aqiri, GEO.hasGeometry, geomiri))
        kg.add((aqiri, GEO.defaultGeometry, geomiri))
        kg.add((geomiri, GEO.asWKT, Literal(row.geometry, datatype=GEO.wktLiteral)))
        kg.add((geomiri, RDF.type, GEO.Geometry))

        # Triplify current principal aquifer attributes
        kg.add((aqiri, _PREFIX['usgs']['hasAqId'], Literal(str(row.OBJECTID_1).zfill(4), datatype=XSD.string)))
        kg.add((aqiri, _PREFIX['usgs']['hasLithology'], _PREFIX['usgs'][f'Lithology.{get_lithology(row.ROCK_NAME)}']))
        kg.add((aqiri, _PREFIX['usgs']['hasAqName'], Literal(row.AQ_NAME, datatype=XSD.string)))

        # Update the processing status to the terminal
        print(f'Processing row {count:4} of {n} : OBJECTID {str(row.OBJECTID_1):4}', end='\r', flush=True)
        count += 1
    logger.info(f'Write principal aquifer triples to {outfile}')
    kg.serialize(outfile, format='turtle')  # Write the completed KG to a .ttl file
