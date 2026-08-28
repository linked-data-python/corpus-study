# Extracted from SAWGraph/water-kg@032ec41357 : datasets/groundwater/il-isgs/IL_ISGS_Aquifer-AqSystem-2ttl.py
# region: process_aquifers_shp2ttl (lines 278-353, stratum coercion_datatype)
# licence of the source repository: see meta.json
import geopandas as gpd
from rdflib import Graph, Literal
from rdflib.namespace import GEO, DCTERMS, OWL, PROV, RDF, RDFS, SDO, XSD
from namespaces import _PREFIX, find_s2_intersects_poly
max_id_length = 4
logger = logging.getLogger(__name__)

def process_aquifers_shp2ttl(br_infile, sg_infile, cg_infile, cgsys_infile, outfile1, outfile2, ids_dict):
    """Triplifies the aquifer data in from a set of .shp files and saves the result as a .ttl file

    :param br_infile: bedrock aquifer .shp file
    :param sg_infile: sand and gravel aquifer .shp file
    :param cg_infile: coarse-grained materials potential aquifer .shp file
    :param cgsys_infile: coarse-grained materials potential aquifer systems .shp file
    :param outfile1: the path and name for the aquifers .ttl file
    :param outfile2: the path and name for the aquifer systems .ttl file
    :param ids_dict: a dictionary of dissolved ids to lists of original ids
    :return:
    """
    logger.info('BEGIN TRIPLIFYING THE AQUIFERS')
    logger.info('Loading the shapefiles')
    gdf_bedrock_aqs = gpd.read_file(br_infile)
    gdf_sandgravel_aqs = gpd.read_file(sg_infile)
    gdf_coarsemtls_aqs = gpd.read_file(cg_infile)
    gdf_coarsemtls_aqsys = gpd.read_file(cgsys_infile)
    list_aqs = [gdf_bedrock_aqs, gdf_sandgravel_aqs, gdf_coarsemtls_aqs]
    logger.info('Intializing the knowledge graph')
    kg_aq = initial_kg(_PREFIX)
    kg_aqsys = initial_kg(_PREFIX)
    logger.info('Creating the triples')
    ordinals = ['first', 'second', 'third', 'fourth']
    count = 0
    for gdf in list_aqs:
        logger.info(f'   Processing {ordinals[count]} set of aquifers (of four)')
        count += 1
        for row in gdf.itertuples():
            if row.aqtype.lower() == 'bedrock':
                init = 'BR'
            elif row.aqtype.lower() == 'sand_gravel':
                init = 'SG'
            elif row.aqtype.lower() == 'coarse-grain_materials':
                init = 'CM'
            fid = int(round(row.fid, 0))
            aqid = init + str(fid).zfill(max_id_length)
            aqiri, geoiri = build_aq_iris(aqid, _PREFIX)
            kg_aq.add((aqiri, RDF.type, _PREFIX['gwml2']['GW_Aquifer']))
            kg_aq.add((aqiri, _PREFIX['il_isgs']['ilSawAqId'], Literal(aqid, datatype=XSD.string)))
            kg_aq.add((aqiri, _PREFIX['saw_water']['aquiferType'], Literal(row.aqtype, datatype=XSD.string)))
            kg_aq.add((aqiri, RDFS.label, Literal(f'A {row.aqtype} aquifer in Illinois', datatype=XSD.string)))
            if row.aqtype.lower() == 'coarse-grain_materials':
                sysid = str(ids_dict[fid])
                aqsysiri = build_aqsys_iris(sysid, _PREFIX)[0]
                kg_aq.add((aqiri, _PREFIX['gwml2']['gwAquiferSystem'], aqsysiri))
                kg_aqsys.add((aqsysiri, _PREFIX['gwml2']['gwAquiferSystemPart'], aqiri))
            kg_aq.add((aqiri, GEO.hasGeometry, geoiri))
            kg_aq.add((aqiri, GEO.defaultGeometry, geoiri))
            kg_aq.add((geoiri, GEO.asWKT, Literal(row.geometry, datatype=GEO.wktLiteral)))
            kg_aq.add((geoiri, RDF.type, GEO.Geometry))
            if 'multipolygon' in str(row.geometry).lower():
                kg_aq.add((geoiri, RDF.type, _PREFIX['sf']['MultiPolygon']))
            else:
                kg_aq.add((geoiri, RDF.type, _PREFIX['sf']['Polygon']))
    logger.info(f'   Processing {ordinals[count]} set of aquifers (of four)')
    for row in gdf_coarsemtls_aqsys.itertuples():
        aqsysiri, geoiri = build_aqsys_iris(row.saw_id, _PREFIX)
        kg_aqsys.add((aqsysiri, RDF.type, _PREFIX['gwml2']['GW_AquiferSystem']))
        kg_aqsys.add((aqsysiri, _PREFIX['il_isgs']['ilSawAqSysId'],
                   Literal('CM' + str(row.saw_id).zfill(max_id_length), datatype=XSD.string)))
        kg_aqsys.add((aqsysiri, RDFS.label, Literal('A system of aquifers in Illinois', datatype=XSD.string)))
        kg_aqsys.add((aqsysiri, RDFS.comment, Literal(
            f'Illinois aquifer systems consist of adjacent potential aquifers in coarse-grained materials within 50ft of the ground surface',
            datatype=XSD.string)))
        kg_aqsys.add((aqsysiri, GEO.hasGeometry, geoiri))
        kg_aqsys.add((aqsysiri, GEO.defaultGeometry, geoiri))
        kg_aqsys.add((geoiri, GEO.asWKT, Literal(row.geometry, datatype=GEO.wktLiteral)))
        kg_aqsys.add((geoiri, RDF.type, GEO.Geometry))
        if 'multipolygon' in str(row.geometry).lower():
            kg_aqsys.add((geoiri, RDF.type, _PREFIX['sf']['MultiPolygon']))
        else:
            kg_aqsys.add((geoiri, RDF.type, _PREFIX['sf']['Polygon']))
    kg_aq.serialize(outfile1, format='ttl')
    kg_aqsys.serialize(outfile2, format='ttl')
    logger.info('TRIPLIFYING COMPLETE AND .ttl FILE CREATED')
