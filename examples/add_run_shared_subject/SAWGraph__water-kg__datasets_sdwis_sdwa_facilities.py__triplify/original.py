# Extracted from SAWGraph/water-kg@032ec41357 : datasets/sdwis/sdwa_facilities.py
# region: triplify (lines 139-182, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS
from rdflib import URIRef, BNode, Literal
prefixes = {}

def triplify(df):
    kg = Initial_KG()
    for idx, row in df.iterrows():
        # get attributes
        facility = get_attributes(row)
        # get iris
        iris = get_iris(facility)
        #print(iris)

        #facility
        kg.add((iris['facility'], prefixes['us_sdwis']['partOf'], iris['PWS']))
        kg.add((iris['facility'], RDF.type, prefixes['us_sdwis']['PWS-SubFeature']))

        kg.add((iris['facility'], RDFS.label, Literal(facility['PWSID']+": "+facility['Facility_Id'], datatype=XSD.string)))
        kg.add((iris['facility'], prefixes['us_sdwis']['hasFacilityId'], Literal(facility['Facility_Id'], datatype=XSD.string)))
        if 'State_Id' in facility.keys():
                kg.add((iris['facility'], prefixes['us_sdwis']['hasStateFacilityId'], Literal(facility['State_Id'], datatype=XSD.string)))
        kg.add((iris['facility'], prefixes['us_sdwis']['hasType'], iris['type']))
        if 'SourceType' in facility.keys():
            kg.add((iris['facility'], prefixes['us_sdwis']['sourceType'], iris['sourceType']))

        #pws
        kg.add((iris['PWS'], RDF.type, prefixes['us_sdwis']['PublicWaterSystem'])) 
        kg.add((iris['PWS'], prefixes['us_sdwis']['hasPart'], iris['facility']))
        if 'Source' in facility.keys():
            if 'Seller_PWSID' in facility.keys():
                #if source is just a connection to another system, make the connection directly 
                kg.add((iris['PWS'], prefixes['us_sdwis']['buysFrom'], iris['seller_PWS']))
                kg.add((iris['seller_PWS'], prefixes['us_sdwis']['sellsTo'], iris['PWS']))
                kg.add((iris['facility'], prefixes['us_sdwis']['connectsTo'], iris['seller_PWS']))

            elif facility['Type'] in ['IG', 'IN', 'RC', 'RS', 'SP', 'WL']: #only count sources that are SW/GW types
                #find permanent (active) sources
                if facility['Availability']=='P': #note some of these may be inactive
                    kg.add((iris['PWS'], prefixes['us_sdwis']['hasPermanentSource'], iris['facility']))
                    kg.add((iris['facility'], prefixes['us_sdwis']['permanentSourceFor'], iris['PWS']))
                else:
                    #TODO this could be expanded to specify other types (Emergency, interim, seasonal, other, unknown)
                    kg.add((iris['PWS'], prefixes['us_sdwis']['hasSource'], iris['facility']))
                    kg.add((iris['facility'], prefixes['us_sdwis']['sourceFor'], iris['PWS']))



    return kg
