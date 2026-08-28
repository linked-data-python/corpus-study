# Extracted from ksahlmann/myno@b67f9de59c : myno-agriculture/virtual-device/aggregatPreload.py
# region: get_event_functions (lines 65-79, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery
initNs = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "base":"http://yang-netconf-mqtt#", "onem2m":"http://www.onem2m.org/ontology/Base_Ontology/base_ontology#",
          "om-2":"http://www.ontology-of-units-of-measure.org/resource/om-2/", "time":"http://www.w3.org/2006/time#"}

def get_event_functions(g):
    print("get_event_functions")

    q = prepareQuery(
        'SELECT ?eventfunc ?topic WHERE { ?device onem2m:hasFunctionality ?eventfunc . ?eventfunc rdf:type base:EventFunctionality. '
        '?serv onem2m:exposesFunctionality ?eventfunc . ?serv onem2m:hasOutputDataPoint ?dp. ?dp  base:mqttTopic ?topic. }',
        initNs)

    result = g.query(q)
    for row in result:
        print(" %s %s" % row)

    print(result.serialize(format='json'))

    return result
