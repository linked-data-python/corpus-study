# Extracted from Haoyu-R/How-to-Manage-TinyML-at-Scale@da05a79f3a : tflite2semantic_user_input.py
# region: tflite2semantic (lines 373-386, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, SDO
nnet = Namespace("http://tinyml-schema.org/networkschema#")
g = Graph()

def addCommonInfo(layer, input_layer=False, output_layer=False):
    g.add((layer, RDF.type, nnet.Layer))
    addTrainable(layer, quantized)
    addLayer(layer, model.OperatorCodes(op.OpcodeIndex()).BuiltinCode())

    if input_layer:
        g.add((layer, nnet.shapeIn, Literal(interpreter.get_input_details()[0]['shape'])))
    if output_layer:
        g.add((layer, nnet.shapeOut, Literal(interpreter.get_output_details()[0]['shape'])))

    if hasActivation:
        addActivation(layer, opt.FusedActivationFunction())
    else:
        addActivation(layer, 0)
