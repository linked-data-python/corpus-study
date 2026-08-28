# Extracted from ksahlmann/myno@b67f9de59c : myno-agriculture/myno-bridge/yang_generator_rdflib.py
# region: parseCtrlFunctionality (lines 509-527, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("yang-generator")

def parseCtrlFunctionality(g, ctrlfuncList):
    print("parseCtrlFunctionality")
    q = prepareQuery(
        'SELECT DISTINCT ?ctrlFunction ?command ?property WHERE { ?ctrlFunction rdf:type onem2m:ControllingFunctionality . ?ctrlFunction onem2m:hasCommand ?command . ?ctrlFunction onem2m:hasThingProperty ?property .}',
        initNs = {"base": "http://yang-netconf-mqtt#", "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
        base = "http://yang-netconf-mqtt#")
    result = g.query(q, initNs={"base": "http://yang-netconf-mqtt#",
                                "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
                     base="http://yang-netconf-mqtt#")

    for row in result:
        logger.debug(" %s %s %s " % row)
        func = {}
        func['id'] = str(row["ctrlFunction"])
        func['commands'] = [str(row["command"])]
        func['properties'] = [str(row["property"])]
        ctrlfuncList.append(func)
        logger.debug(ctrlfuncList)
    return ctrlfuncList
