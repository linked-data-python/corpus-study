# Extracted from ksahlmann/myno@b67f9de59c : myno-agriculture/virtual-device/aggregatPreload.py
# region: get_event_functions (lines 65-79, stratum sparql_literal)
# licence of the source repository: see meta.json
initNs = {"base":"http://yang-netconf-mqtt#", "onem2m":"http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"}

def get_event_functions(g):
    print("get_event_functions")

    result = g.query("""
    SELECT ?eventfunc ?topic WHERE {
        ?device onem2m:hasFunctionality ?eventfunc .
        ?eventfunc a base:EventFunctionality .
        ?serv onem2m:exposesFunctionality ?eventfunc ;
            onem2m:hasOutputDataPoint/base:mqttTopic ?topic .
    }""", initNs=initNs)
    for row in result:
        print(" %s %s" % row)

    print(result.serialize(format='json'))

    return result
