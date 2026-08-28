# Extracted from SAWGraph/water-kg@032ec41357 : datasets/sdwis/pws_serviceAreas_cws-ncws.py
# region: triplify_pws_data (lines 232-276, stratum add_isolated)
# licence of the source repository: see meta.json
import pandas as pd
from rdflib.namespace import GEO, OWL, PROV, RDF, RDFS, SDO, XSD
from rdflib import Graph, Literal, Namespace, URIRef
from namespaces import _PREFIX
ontologyIRI = URIRef(ontologyStem)
logger = logging.getLogger(__name__)

def triplify_pws_data(kg: Graph, df: pd.DataFrame) -> Graph:
    """
        Takes a Graph and a dataframe of public water system data for a specific state,
        writes new triples for each row (public water system) to the Graph, and
        returns the updated Graph

        :param kg: a Graph of public water system triples for a given state
        :param df: a dataframe of public water system data
        :return: an updated Graph
    """
    logger.info('      Triplifying PWS data')
    for row in df.itertuples():
        attributes = get_pws_attributes(row)
        iris = get_iris(attributes)
        kg.add((iris['pws'], RDF.type, _PREFIX['us_sdwis'][f'PublicWaterSystem-{attributes['pwstype']}']))
        kg.add((iris['pws'], RDFS.isDefinedBy, ontologyIRI))
        # kg.add((iris['pws'], _PREFIX['us_sdwis']['pwsId'], Literal(attributes['pwsid'], datatype=XSD.string)))
        kg.add((iris['pws'], _PREFIX['us_sdwis']['hasActivity'], Literal(attributes['activity'], datatype=XSD.string)))
        kg.add((iris['pws'], _PREFIX['us_sdwis']['populationServed'], Literal(attributes['popserved'], datatype=XSD.integer)))
        if 'name' in attributes:
            kg.add((iris['pws'], _PREFIX['us_sdwis']['pwsName'], Literal(attributes['name'], datatype=XSD.string)))
            kg.add((iris['pws'], RDFS.label, Literal(attributes['name'], datatype=XSD.string)))
        else:
            kg.add((iris['pws'], RDFS.label, Literal(attributes['pwsid'], datatype=XSD.string)))
        if 'deactive_date' in attributes:
            kg.add((iris['pws'], _PREFIX['us_sdwis']['deactivationDate'], Literal(attributes['deactive_date'], datatype=XSD.date)))
        if 'gwsw' in attributes:
            kg.add((iris['pws'], RDF.type, _PREFIX['us_sdwis'][f'PublicWaterSystem-{attributes['gwsw']}']))
        if 'ownertype' in attributes:
            kg.add((iris['pws'], _PREFIX['us_sdwis']['hasOwnership'], Literal(attributes['ownertype'], datatype=XSD.string)))
        if 'source' in attributes:
            kg.add((iris['pws'], _PREFIX['us_sdwis']['primarySourceType'], _PREFIX['us_sdwis'][f'PWS-WaterSourceType.{row.PRIMARY_SOURCE_CODE}']))
        #     kg.add((iris['pws'], _PREFIX['us_sdwis']['primarySource'], Literal(attributes['source'], datatype=XSD.string)))
        if 'connections' in attributes:
            kg.add((iris['pws'], _PREFIX['us_sdwis']['serviceConnections'], Literal(attributes['connections'], datatype=XSD.integer)))
        if 'firstreport' in attributes:
            kg.add((iris['pws'], _PREFIX['us_sdwis']['firstReport'], Literal(attributes['firstreport'], datatype=XSD.date)))
        if 'lastreport' in attributes:
            kg.add((iris['pws'], _PREFIX['us_sdwis']['lastReport'], Literal(attributes['lastreport'], datatype=XSD.date)))
        # if 'sourceprotection' in attributes:
        #     kg.add((iris['pws'], _PREFIX['us_sdwis']['sourceProtection'], Literal(attributes['sourceprotection'], datatype=XSD.date)))
        # if 'cdsid' in attributes:
        #     kg.add((iris['pws'], _PREFIX['us_sdwis']['cdsId'], Literal(attributes['cdsid'], datatype=XSD.date)))
    logger.info(f'      PWS data triplified')
    return kg
