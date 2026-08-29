# Extracted from ksahlmann/myno@b67f9de59c : myno-agriculture/myno-bridge/yang_generator_rdflib.py
# region: parseServices (lines 399-448, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("yang-generator")

def parseServices(g, serviceList):
    print("parseServices")

    q = prepareQuery(
        'SELECT DISTINCT ?services  ?functions  ?subservices  ?operations '
        'WHERE { ?device onem2m:hasService ?services . ?services onem2m:hasSubService ?subservices .   ?services  onem2m:exposesFunctionality ?functions . '
        ' OPTIONAL { ?services onem2m:hasOperation ?operations . } } ORDER BY DESC(?functions) ',
        initNs={"base": "http://yang-netconf-mqtt#", "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
        base="http://yang-netconf-mqtt#")
    result = g.query(q)

    functionalities = set([])
    operations = set([])
    subservices = set([])
    #outDps = []
    for row in result:
        logger.debug(" %s %s %s %s" % row)
        service = {}
        service['id'] = str(row["services"])
        functionalities.add(str(row["functions"]))
        #functionalities.add(str(row["subfunctions"]))
        subservices.add(str(row["subservices"]))
        operations.add(str(row["operations"]))
        #operations.add(str(row["suboperations"]))
    service['functionalities'] = list(functionalities)
    service['operations'] = list(operations)
    service['subservices'] = list(subservices)
    logger.debug(service)
    serviceList.append(service)

    # Type 2 subservices with outDPs
    q = prepareQuery(
        'SELECT DISTINCT ?subservices ?functions ?outDps ?operations '
        'WHERE { ?services onem2m:hasSubService ?subservices . ?subservices  onem2m:exposesFunctionality ?functions . OPTIONAL {?subservices onem2m:hasOutputDataPoint ?outDps .} OPTIONAL{?subservices onem2m:hasOperation ?operations . } }  ORDER BY DESC(?functions) ',
        initNs={"base": "http://yang-netconf-mqtt#", "onem2m": "http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"},
        base="http://yang-netconf-mqtt#")
    result = g.query(q)

    for row in result:
        logger.debug(" %s %s %s %s" % row)
        service = {}
        service['id'] = str(row["subservices"])
        service['functionalities'] = [str(row["functions"])]
        #if(str(row["outDps"])):
        service['outDps'] = [str(row["outDps"])]
        if (str(row["operations"])):
            service['operations'] = [str(row["operations"])]  # new
        logger.debug(service)
        serviceList.append(service)
    return serviceList
