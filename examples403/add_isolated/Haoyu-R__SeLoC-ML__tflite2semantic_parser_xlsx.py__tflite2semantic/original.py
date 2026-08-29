# Extracted from Haoyu-R/SeLoC-ML@5ecc52c25e : tflite2semantic_parser_xlsx.py
# region: tflite2semantic (lines 393-411, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef, Namespace
from context_shim import idOfNN, neuralNetwork, graph, j, addCommonInfo
nnet = Namespace("https://w3id.org/tinyml-schema/neural-network-schema#")
g = Graph()

if j == 0:
    # First layer is input layer
    inputLayer = URIRef("https://w3id.org/tinyml-schema/neural-network-schema/neuralnetwork/inputLayer_" + idOfNN)
    g.add((neuralNetwork, nnet.inputLayer, inputLayer))
    addCommonInfo(inputLayer, input_layer=True)
    g.add((inputLayer, nnet.hasIndex, Literal(j+1)))
elif j == (graph.OperatorsLength() - 1):
    # Last layer is output layer
    outputLayer = URIRef("https://w3id.org/tinyml-schema/neural-network-schema/neuralnetwork/outputLayer_" + idOfNN)
    g.add((neuralNetwork, nnet.outputLayer, outputLayer))
    addCommonInfo(outputLayer, output_layer=True)
    g.add((outputLayer, nnet.hasIndex, Literal(j+1)))
else:
    middleLayer = URIRef("https://w3id.org/tinyml-schema/neural-network-schema/neuralnetwork/middleLayer_" + "{}_".format(j) + idOfNN)
    g.add((neuralNetwork, nnet.middleLayer, middleLayer))
    g.add((middleLayer, nnet.hasIndex, Literal(j)))
    addCommonInfo(middleLayer)
    # g.add((middleLayer, RDFS.label, Literal("middleLayer_" + idOfNN + "_{}".format(j))))
    g.add((middleLayer, nnet.hasIndex, Literal(j)))
