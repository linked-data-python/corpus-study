# Extracted from Haoyu-R/How-to-Manage-TinyML-at-Scale@da05a79f3a : tflite2semantic_user_input.py
# region: tflite2semantic (lines 373-386, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, SDO
from tflite_context import (
    model, op, opt, interpreter, quantized, hasActivation,
    make_addcommoninfo_helpers,
)
nnet = Namespace("http://tinyml-schema.org/networkschema#")
g = Graph()
addTrainable, addLayer, addActivation = make_addcommoninfo_helpers(g)

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

# Explicit invocations added so the region's effect on `g` is observable
# (entry=None module-state oracle): the real code calls addCommonInfo this
# same way, once per layer, at lines 391 (input_layer=True), 397
# (output_layer=True) and 404 (neither) -- see meta.json and driver.py.
addCommonInfo(URIRef("http://tinyml-schema.org/neuralnetwork/inputLayer_x"), input_layer=True)
addCommonInfo(URIRef("http://tinyml-schema.org/neuralnetwork/outputLayer_x"), output_layer=True)
addCommonInfo(URIRef("http://tinyml-schema.org/neuralnetwork/middleLayer_x_0"))
