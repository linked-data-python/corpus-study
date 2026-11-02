# Extracted from Haoyu-R/SeLoC-ML@5ecc52c25e : tflite2semantic_user_input.py
# region: tflite2semantic (lines 106-111, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, SDO
from context_shim import addHardware, idOfNN, inputOfNN, sensor_info_, sensor_list_  # context shim -- see meta.json
ssn_extend = Namespace("https://w3id.org/tinyml-schema/neural-network-schema/ssn_extend/")
sosa_extend = Namespace("https://w3id.org/tinyml-schema/neural-network-schema/sosa_extend/")
g = Graph()

for i, value in enumerate(sensor_list_):
    sensorOfNN = URIRef(f"https://w3id.org/tinyml-schema/neural-network-schema/neuralnetwork/sensor_{i + 1}_{idOfNN}")
    g += [
        (sensorOfNN, RDF.type, addHardware(value)),
        (sensorOfNN, RDF.type, SDO.Sensor),
        (sensorOfNN, sosa_extend.hasSensorInfo, Literal(sensor_info_)),
        (sensorOfNN, ssn_extend.provideInput, inputOfNN),
    ]
