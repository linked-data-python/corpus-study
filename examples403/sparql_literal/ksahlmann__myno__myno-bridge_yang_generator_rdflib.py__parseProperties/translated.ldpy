# Extracted from ksahlmann/myno@b67f9de59c : myno-bridge/yang_generator_rdflib.py
# region: parseProperties (lines 836-896, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery

def parseProperties(g, propList):
    print("parseProperties")
    # part 1 ThingProperty
    q = prepareQuery(
        'SELECT DISTINCT ?property ?type ?value '
        'WHERE { ?property rdf:type onem2m:ThingProperty . ?property rdf:type ?type. ?property onem2m:hasValue ?value . }',
        initNs = {"base": "http://yang-netconf-mqtt#", "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
        base = "http://yang-netconf-mqtt#")
    result = g.query(q, initNs={"base": "http://yang-netconf-mqtt#",
                                "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"}, base="http://yang-netconf-mqtt#")

    for row in result:
        print(" %s %s %s " % row)
        if str(row["type"]) != "http://www.w3.org/2002/07/owl#NamedIndividual":
            prop = {}
            prop['id'] = str(row["property"])
            prop['type'] = str(row["type"])
            prop['values'] = [str(row["value"])]
            propList.append(prop)

    # part 2 YangDescription
    q = prepareQuery(
        'SELECT DISTINCT ?property ?type ?value '
        'WHERE { ?property rdf:type base:YangDescription. ?property rdf:type ?type. ?property onem2m:hasValue ?value. }',
            initNs={"base": "http://yang-netconf-mqtt#",
                    "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
            base="http://yang-netconf-mqtt#")
    result = g.query(q, initNs={"base": "http://yang-netconf-mqtt#", "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
            base="http://yang-netconf-mqtt#")

    for row in result:
        print(" %s %s %s " % row)
        if str(row["type"]) != "http://www.w3.org/2002/07/owl#NamedIndividual":
            prop = {}
            prop['id'] = str(row["property"])
            prop['type'] = str(row["type"])
            prop['values'] = [str(row["value"])]
            propList.append(prop)

    # part 3 OperationStateDescriptions hasDataRestriction_pattern
    q = prepareQuery(
        'SELECT DISTINCT  ?property ?type ?dataRestrictions ' 
        'WHERE { ?property rdf:type base:YangDescription. ?property rdf:type ?type. ?property onem2m:hasDataRestriction_pattern ?dataRestrictions. } ORDER BY ?dataRestrictions ',
            initNs={"base": "http://yang-netconf-mqtt#", "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
            base="http://yang-netconf-mqtt#")
    result = g.query(q, initNs={"base": "http://yang-netconf-mqtt#", "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
            base="http://yang-netconf-mqtt#")

    dataRestriction = []
    for row in result:
        print(" %s %s %s " % row)
        if str(row["type"]) != "http://www.w3.org/2002/07/owl#NamedIndividual":
            prop = {}
            prop['id'] = str(row["property"])
            prop['type'] = str(row["type"])
            dataRestriction.append({'@value': str(row["dataRestrictions"])})
            prop['dataRestrictions'] = dataRestriction
            propList.append(prop)

    print(propList)
    return propList
