# Extracted from SAWGraph/water-kg@032ec41357 : datasets/sdwis/sdwa_pws.py
# region: triplify (lines 192-239, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, XMLNS, XSD, RDF, RDFS
from rdflib import URIRef, BNode, Literal
from shim import prefixes, Initial_KG, get_attributes, get_iris

def triplify(df):
    kg = Initial_KG()
    us_sdwis = prefixes['us_sdwis']
    for idx, row in df.iterrows():
        # get attributes
        pws = get_attributes(row)
        # get iris
        iris = get_iris(pws)
        pws_iri = iris['PWS']
        #print(iris)

        #pws
        #key data properties
        kg += [
            (pws_iri, RDF.type, us_sdwis.PublicWaterSystem),
            (pws_iri, us_sdwis.populationServed, Literal(pws['PopulationServed'], datatype=XSD.int)),
            (pws_iri, us_sdwis.serviceConnections, Literal(pws['Connections'], datatype=XSD.int)),
            # TODO Activity code - class?
            (pws_iri, us_sdwis.hasActivity, Literal(pws['ActivityCodeLong'], datatype=XSD.string)),
            #TODO season begin/end What datatype for recurring day-month date?
            (pws_iri, us_sdwis.firstReport, Literal(pws['FirstReport'], datatype=XSD.date)),
        ]
        if pws['Type'] != "NP":
            kg.add((pws_iri, RDF.type, us_sdwis['PublicWaterSystem-' + pws['Type']]))
        for key in ('Transient', 'GWSW'): #See also primarySourceType
            if key in pws:
                kg.add((pws_iri, RDF.type, us_sdwis['PublicWaterSystem-' + pws[key]]))

        #extra properties
        for key, predicate, datatype in (
            ('Name', us_sdwis.pwsName, XSD.string),
            ('Name', RDFS.label, XSD.string),
            ('Deactivation', us_sdwis.deactivationDate, XSD.date),
            ('Owner', us_sdwis.hasOwnership, XSD.string),
            ('LastReport', us_sdwis.lastReport, XSD.date),
        ):
            if key in pws:
                kg.add((pws_iri, predicate, Literal(pws[key], datatype=datatype)))
        if 'SourceType' in pws:
            #kg.add((iris['PWS'], prefixes['us_sdwis']['primarySource'], Literal(pws['Source'], datatype=XSD.string))) #old literal version
            kg.add((pws_iri, us_sdwis.primarySourceType, iris['SourceType'])) #controlled vocab

        #object properties
        ##combined distribution system
        if 'CDSID' in pws:
            kg += [(iris['CDS'], RDF.type, us_sdwis.CombinedDistributionSystem),
                   (pws_iri, us_sdwis.inCombinedSystem, iris['CDS'])]

    return kg
