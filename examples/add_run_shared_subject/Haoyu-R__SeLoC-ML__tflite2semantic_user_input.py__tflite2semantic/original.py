# Extracted from Haoyu-R/SeLoC-ML@5ecc52c25e : tflite2semantic_user_input.py
# region: tflite2semantic (lines 106-111, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, SDO
ssn_extend = Namespace("https://w3id.org/tinyml-schema/neural-network-schema/ssn_extend/")
sosa_extend = Namespace("https://w3id.org/tinyml-schema/neural-network-schema/sosa_extend/")
g = Graph()

for i, value in enumerate(sensor_list_):
    sensorOfNN = URIRef("https://w3id.org/tinyml-schema/neural-network-schema/neuralnetwork/sensor" + "_" + "{}".format(i + 1) + "_" + idOfNN)
    g.add((sensorOfNN, RDF.type, addHardware(value)))
    g.add((sensorOfNN, RDF.type, SDO.Sensor))
    g.add((sensorOfNN, sosa_extend.hasSensorInfo, Literal(sensor_info_)))
    g.add((sensorOfNN, ssn_extend.provideInput, inputOfNN))
