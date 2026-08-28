# Extracted from ksahlmann/myno@b67f9de59c : myno-agriculture/myno-bridge/yang_generator_rdflib.py
# region: parseDevices (lines 375-397, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("yang-generator")
initNs = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "base":"http://yang-netconf-mqtt#", "onem2m":"http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"}
generic_id = '@id'

def parseDevices(g, deviceList):
    print("parseDevices")
    q = prepareQuery(
        'SELECT DISTINCT ?device ?services ?functions ?properties WHERE {?device rdf:type onem2m:Device . ?device onem2m:hasFunctionality ?functions . ?device onem2m:hasService ?services . ?device onem2m:hasThingProperty ?properties . }',
        initNs)
    result = g.query(q)

    device = {}
    services = set([])
    functionalities = set([])
    properties = set([])
    for row in result:
        logger.debug(" %s %s %s %s" % row)
        device[generic_id] = str(row["device"])
        services.add(str(row["services"]))
        functionalities.add(str(row["functions"]))
        properties.add(str(row["properties"]))
    device['services'] = list(services)
    device['functionalities'] = list(functionalities)
    device['properties'] = list(properties)
    logger.debug(device)
    deviceList.append(device)
    return deviceList
