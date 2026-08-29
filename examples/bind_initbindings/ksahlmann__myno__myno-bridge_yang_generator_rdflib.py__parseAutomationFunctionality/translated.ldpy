# Extracted from ksahlmann/myno@b67f9de59c : myno-bridge/yang_generator_rdflib.py
# region: parseAutomationFunctionality (lines 541-559, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery

def parseAutomationFunctionality(g, autofuncList):
    print("parseAutomationFunctionality")
    q = prepareQuery(
        'SELECT DISTINCT ?autoFunction ?command ?property WHERE { ?autoFunction rdf:type base:AutomationFunctionality . ?autoFunction onem2m:hasCommand ?command . ?autoFunction onem2m:hasThingProperty ?property .}',
        initNs = {"base": "http://yang-netconf-mqtt#", "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
        base = "http://yang-netconf-mqtt#")
    result = g.query(q, initNs={"base": "http://yang-netconf-mqtt#",
                                "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
                     base="http://yang-netconf-mqtt#")

    for row in result:
        print(" %s %s %s " % row)
        func = {}
        func['id'] = str(row["autoFunction"])
        func['commands'] = [str(row["command"])]
        func['properties'] = [str(row["property"])]
        autofuncList.append(func)
        print(autofuncList)
    return autofuncList
