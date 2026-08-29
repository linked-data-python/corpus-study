# Extracted from ksahlmann/myno@b67f9de59c : myno-agriculture/myno-bridge/kafka/json_generator.py
# region: generate_json_kafka (lines 24-73, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery
logger = logging.getLogger("json-generator")
base = "http://yang-netconf-mqtt#"
initNs = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "base":"http://yang-netconf-mqtt#", "onem2m":"http://www.onem2m.org/ontology/Base_Ontology/base_ontology#", "om-2":"http://www.ontology-of-units-of-measure.org/resource/om-2/"}

def generate_json_kafka(json_str):
    print("parseDevicesJson")

    raw_data = {}

    g = Graph()
    g.parse(data=json_str, format="json-ld", base="http://yang-netconf-mqtt#")

    # q = prepareQuery(
    #     'SELECT DISTINCT ?device ?properties ?functions ?mqttTopic  WHERE {?device rdf:type onem2m:Device . ?device onem2m:hasThingProperty ?properties .  ?device onem2m:hasFunctionality ?functions .  ?functions rdf:type onem2m:MeasuringFunctionality .  '
    #     '?services onem2m:exposesFunctionality ?functions . ?services onem2m:hasOutputDataPoint ?outDp . ?outDp  base:mqttTopic ?mqttTopic . } ', initNs)
    # result = g.query(q)
    #
    # for row in result:
    #     print(" %s %s %s %s" % row)
        #str(row["device"])


    # only device properties
    q = prepareQuery(
        'SELECT DISTINCT ?device ?properties ?value WHERE {?device rdf:type onem2m:Device . ?device onem2m:hasThingProperty ?properties .  ?properties onem2m:hasValue ?value . }', initNs)
    result = g.query(q)
    for row in result:
        logger.debug(" %s %s %s" % row)
        if(str(row["properties"]) == base + "deviceUuid"):
            logger.debug(str(row["properties"]))
            raw_data["device-uuid"] = str(row["value"])

    # TODO add location
    raw_data["location"] = "building4/room2.02"

    # only functions and mqtt topics
    q = prepareQuery(
        'SELECT DISTINCT ?functions ?mqttTopic ?units WHERE {?functions rdf:type onem2m:MeasuringFunctionality .  ?services onem2m:exposesFunctionality ?functions . ?services onem2m:hasOutputDataPoint ?outDp . ?outDp  base:mqttTopic ?mqttTopic . ?outDp om-2:hasUnit ?units .} ', initNs)
    #'SELECT DISTINCT ?functions ?mqttTopic ?units WHERE {?functions rdf:type onem2m:MeasuringFunctionality .  ?services onem2m:exposesFunctionality ?functions . ?services onem2m:hasOutputDataPoint ?outDp . ?outDp  base:mqttTopic ?mqttTopic . ?functions om-2:hasUnit ?units .} ', initNs)
    result = g.query(q)

    sensors_list = []
    for row in result:
        logger.debug(" %s %s %s" % row)
        sens_dict = {}
        sens_dict["mqtt-topic"] = str(row["mqttTopic"])
        sens_dict["units"] = str(row["units"]).split("/om-2/")[1]

        sensors_list.append(sens_dict)

    raw_data["sensors"] = sensors_list

    logger.debug(raw_data)
    build_json(raw_data)
