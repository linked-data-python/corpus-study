# Extracted from SAWGraph/water-kg@032ec41357 : datasets/sdwis/pws_serviceAreas_cws-ncws.py
# region: triplify_service_area_data (lines 428-450, stratum add_in_loop)
# licence of the source repository: see meta.json
import pandas as pd
from rdflib.namespace import GEO, OWL, PROV, RDF, RDFS, SDO, XSD
from rdflib import Graph, Literal, Namespace, URIRef
from namespaces import _PREFIX
ontologyIRI = URIRef(ontologyStem)
logger = logging.getLogger(__name__)

def triplify_service_area_data(kg: Graph, df: pd.DataFrame) -> Graph:
    """
        Takes a Graph and a dataframe of public water system service area data for a specific state,
        writes new triples for each row (public water system) to the Graph, and
        returns the updated Graph

        :param kg: a Graph of public water system triples for a given state
        :param df: a dataframe of public water system service area data
        :return: an updated Graph
    """
    logger.info('      Triplifying PWS service area data')
    ref_codes = create_refcode_lookup()
    for row in df.itertuples():
        attributes = get_service_area_attributes(row)
        iris = get_iris(attributes, ref_codes)
        kg.add((iris['pws'], RDF.type, _PREFIX['us_sdwis']['PublicWaterSystem']))
        kg.add((iris['pws'], RDFS.isDefinedBy, ontologyIRI))
        kg.add((iris['pws'], _PREFIX['us_sdwis']['serviceArea'], iris['sa']))
        kg.add((iris['sa'], RDF.type, _PREFIX['us_sdwis']['PWS-ServiceArea']))
        if 'satype' in attributes:
            kg.add((iris['sa'], _PREFIX['us_sdwis']['serviceAreaType'], iris['satype']))
    logger.info(f'      PWS service area data triplified')
    return kg
