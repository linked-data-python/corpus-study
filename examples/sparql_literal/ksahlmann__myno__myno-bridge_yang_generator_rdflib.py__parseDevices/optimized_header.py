# Extracted from ksahlmann/myno@b67f9de59c : myno-bridge/yang_generator_rdflib.py
# region: parseDevices (lines 366-388, stratum sparql_literal)
# licence of the source repository: see meta.json
initNs = {"onem2m":"http://www.onem2m.org/ontology/Base_Ontology/base_ontology#"}
generic_id = '@id'

def parseDevices(g, deviceList):
    print("parseDevices")
    device = {}
    services, functionalities, properties = set(), set(), set()
    for row in g.query("""
    SELECT DISTINCT ?device ?services ?functions ?properties WHERE {
        ?device a onem2m:Device ; onem2m:hasFunctionality ?functions ;
            onem2m:hasService ?services ; onem2m:hasThingProperty ?properties .
    }""", initNs=initNs):
        print(" %s %s %s %s" % row)
        device[generic_id] = str(row.device)
        services.add(str(row.services))
        functionalities.add(str(row.functions))
        properties.add(str(row.properties))
    device.update(services=list(services), functionalities=list(functionalities),
                  properties=list(properties))
    print(device)
    deviceList.append(device)
    return deviceList
