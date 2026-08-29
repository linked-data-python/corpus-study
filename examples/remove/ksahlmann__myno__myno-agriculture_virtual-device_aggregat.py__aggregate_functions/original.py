# Extracted from ksahlmann/myno@b67f9de59c : myno-agriculture/virtual-device/aggregat.py
# region: aggregate_functions (lines 167-187, stratum remove)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS
from rdflib.plugins.sparql import prepareQuery
from rdflib.namespace import RDF, OWL, XSD
initNs = {"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#", "base":"http://yang-netconf-mqtt#", "onem2m":"http://www.onem2m.org/ontology/Base_Ontology/base_ontology#",
          "om-2":"http://www.ontology-of-units-of-measure.org/resource/om-2/", "time":"http://www.w3.org/2006/time#"}
n = Namespace("http://yang-netconf-mqtt#")
uriref_control_func = URIRef(onem2m + 'ControllingFunction')
uriref_prop_expFunc = URIRef(onem2m + 'exposesFunctionality')
uriref_prop_hasfunc = URIRef(onem2m + 'hasFunctionality')

def aggregate_functions(vdg):
    print("aggregate_functions")

    # TODO aggregate functions like one switchAllOn and switchAllOff and map
    # TODO kann nichts finden, weil in device1 verschiedene namespaces bei den instanzen verwendet werden. WARUM und WAS IST RICHTIG?
    q = prepareQuery(
        'SELECT ?controlfunc WHERE { ?device onem2m:hasFunctionality ?controlfunc . ?controlfunc rdf:type onem2m:ControllingFunction . FILTER REGEX (str(?controlfunc), "off", "i").}',
        initNs)
    result = vdg.query(q)
    if len(result) > 0:
        for row in result:
            print("off %s" % row)
            line = row['controlfunc']
            vdg.remove((n.virtualDevice, uriref_prop_hasfunc, line))
            vdg.remove((n.servVDnetconf, uriref_prop_expFunc, line))
            vdg.remove((line, RDF.type, uriref_control_func))

            # replace controllingFunction
            vdg.add((n.virtualDevice, uriref_prop_hasfunc, line + 'All'))
            vdg.add((n.servVDnetconf, uriref_prop_expFunc, line + 'All'))
            vdg.add((line + 'All', RDF.type, uriref_control_func))
