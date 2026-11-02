# Extracted from SAWGraph/water-kg@032ec41357 : datasets/surface_water/US_NHD_Waterbody_HUCxx-2ttl.py
# region: process_waterbodies_shp2ttl (lines 128-177, stratum add_in_loop)
# licence of the source repository: see meta.json
import pandas as pd
from rdflib import Literal, URIRef
from rdflib.namespace import GEO, RDF, RDFS, SDO, XSD
import logging
from context_shim import shapely, _PREFIX
from context_shim import load_waterbodies, initial_kg, build_iris
ontologyStem = 'http://nhdplusv2.spatialai.org/v1/nhdplusv2-wb-data'
ontologyIRI = URIRef(ontologyStem)
logger = logging.getLogger(__name__)

def process_waterbodies_shp2ttl(vpunum, infile, outfile):
    """Triplifies the water body data in a .shp file and saves the result as a .ttl file

    :param infile: a .shp file with NHD water body data
    :param outfile: the path and name for the .ttl file
    :return:
    """
    # Read NHDWaterbody to a GeoDataframe
    gdf_waterbody = load_waterbodies(vpunum, infile)

    # KWG script doesn't like 3D polygons so this forces them all to 2D
    #   The Z value is set to 0 in NHDWaterbody so nothing is lost from this process
    logger.info('Force geometries to 2D')
    for row in gdf_waterbody.itertuples():
        gdf_waterbody._set_value(row.Index, 'GEOMETRY',
                                 shapely.wkb.loads(shapely.wkb.dumps(row.GEOMETRY, output_dimension=2)))
    logger.info('Intialize RDFLib Graph')
    kg = initial_kg(_PREFIX, vpunum)  # Create an empty Graph() with SAWGraph namespaces
    logger.info(f'Triplify HUC{vpunum} water bodies')
    for row in gdf_waterbody.itertuples():
        # Get IRIs for the current NHDWaterbody and its geometry
        bodyiri, geomiri = build_iris(row.COMID, _PREFIX)
        if 'estuary' in row.FTYPE.lower():
            hyf_class = 'HY_Estuary'
        elif 'lake' in row.FTYPE.lower():
            hyf_class = 'HY_Lake'
        elif 'reservoir' in row.FTYPE.lower():
            hyf_class = 'HY_Impoundment'
        else:
            hyf_class = 'HY_WaterBody'
        kg += [(bodyiri, RDF.type, _PREFIX['hyf'][hyf_class]),
               (bodyiri, RDFS.isDefinedBy, ontologyIRI),
               # Triplify the geometry for the current NHDWaterbody
               (bodyiri, GEO.hasGeometry, geomiri),
               (bodyiri, GEO.defaultGeometry, geomiri),
               (geomiri, GEO.asWKT, Literal(row.GEOMETRY, datatype=GEO.wktLiteral)),
               (geomiri, RDF.type, GEO.Geometry)]

        # Triplify current NHDWaterbody attributes
        if not pd.isnull(row.GNIS_NAME):
            kg.add((bodyiri, SDO.name, Literal(row.GNIS_NAME, datatype=XSD.string)))
        kg += [(bodyiri, _PREFIX['us_nhdplusv2'][prop], Literal(str(value), datatype=XSD.string))
               for prop, value in (('hasCOMID', row.COMID), ('hasFTYPE', row.FTYPE),
                                   ('hasFCODE', row.FCODE), ('hasReachCode', row.REACHCODE))]
        if row.REACHCODE is not None:
            kg.add((bodyiri, _PREFIX['us_wbd']['containingHUC'], _PREFIX['us_wbd_data']['d.HUC8.' + str(row.REACHCODE)[:8]]))

    logger.info(f'Write HUC{vpunum} water body triples to {outfile}')
    kg.serialize(outfile, format='turtle')  # Write the completed KG to a .ttl file
