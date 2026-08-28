# Extracted from SAWGraph/water-kg@032ec41357 : datasets/sdwis/sdwa_pws.py
# region: triplify (lines 192-239, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS
from rdflib import URIRef, BNode, Literal
prefixes = {}

def triplify(df):
    kg = Initial_KG()
    for idx, row in df.iterrows():
        # get attributes
        pws = get_attributes(row)
        # get iris
        iris = get_iris(pws)
        #print(iris)

        #pws
        kg.add((iris['PWS'], RDF.type, prefixes['us_sdwis']['PublicWaterSystem']))
        if pws['Type'] != "NP":
            kg.add((iris['PWS'], RDF.type, prefixes['us_sdwis'][str('PublicWaterSystem' + '-' + pws['Type'])])) 
        if 'Transient' in pws.keys():
            kg.add((iris['PWS'], RDF.type, prefixes['us_sdwis'][str('PublicWaterSystem' + '-' + pws['Transient'])]))
        if 'GWSW' in pws.keys():
            kg.add((iris['PWS'], RDF.type, prefixes['us_sdwis'][str('PublicWaterSystem' + '-' + pws['GWSW'])])) #See also primarySourceType
        if 'Name' in pws.keys():
            kg.add((iris['PWS'], prefixes['us_sdwis']['pwsName'], Literal(pws['Name'], datatype=XSD.string)))
            kg.add((iris['PWS'], RDFS.label, Literal(pws['Name'], datatype=XSD.string)))

        #key data properties
        kg.add((iris['PWS'], prefixes['us_sdwis']['populationServed'], Literal(pws['PopulationServed'], datatype=XSD.int)))
        kg.add((iris['PWS'], prefixes['us_sdwis']['serviceConnections'], Literal(pws['Connections'], datatype=XSD.int)))
        # TODO Activity code - class?
        kg.add((iris['PWS'], prefixes['us_sdwis']['hasActivity'], Literal(pws['ActivityCodeLong'], datatype=XSD.string)))
        #TODO season begin/end What datatype for recurring day-month date?

        #extra properties
        if 'Deactivation' in pws.keys():
            kg.add((iris['PWS'], prefixes['us_sdwis']['deactivationDate'], Literal(pws['Deactivation'], datatype=XSD.date)))
        if 'Owner' in pws.keys():
            kg.add((iris['PWS'],prefixes['us_sdwis']['hasOwnership'], Literal(pws['Owner'], datatype=XSD.string)))
        if 'SourceType' in pws.keys():
            #kg.add((iris['PWS'], prefixes['us_sdwis']['primarySource'], Literal(pws['Source'], datatype=XSD.string))) #old literal version
            kg.add((iris['PWS'], prefixes['us_sdwis']['primarySourceType'], iris['SourceType'])) #controlled vocab
        kg.add((iris['PWS'], prefixes['us_sdwis']['firstReport'], Literal(pws['FirstReport'], datatype=XSD.date )))
        if 'LastReport' in pws.keys():
            kg.add((iris['PWS'], prefixes['us_sdwis']['lastReport'], Literal(pws['LastReport'], datatype=XSD.date)))


        #object properties
        ##combined distribution system
        if 'CDSID' in pws.keys():
            kg.add((iris['CDS'], RDF.type, prefixes['us_sdwis']['CombinedDistributionSystem']))
            kg.add((iris['PWS'], prefixes['us_sdwis']['inCombinedSystem'], iris['CDS']))

    return kg
