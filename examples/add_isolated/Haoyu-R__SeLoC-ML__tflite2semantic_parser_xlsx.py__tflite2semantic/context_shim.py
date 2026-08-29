# Context shim (see meta.json), for Haoyu-R/SeLoC-ML@5ecc52c25e :
# tflite2semantic_parser_xlsx.py.
#
# The extracted region (lines 393-411) is the tail of the per-layer
# if/elif/else inside tflite2semantic()'s "for j in range(graph.
# OperatorsLength())" loop. idOfNN, neuralNetwork, j and graph are locals of
# the enclosing function/loop that the line-range extraction did not
# capture; addCommonInfo is a nested function defined a few lines above the
# region (lines 376-391 of the source file) that the extraction likewise did
# not capture.
#
# idOfNN/neuralNetwork are reproduced with the file's own IRI scheme
# (lines 55 and 67 of the source file). graph is a minimal stand-in
# exposing only .OperatorsLength(), the single method this region calls on
# it, set (together with j) so the "middle layer" branch runs -- the
# richest of the three (two distinct add() calls, one of them repeated
# verbatim right after addCommonInfo(), apparently a copy-paste artefact of
# the original code that the translation preserves rather than "fixes").
#
# addCommonInfo is stubbed inert. Its real body (lines 376-391) reads the
# parsed .tflite model, the TF interpreter, and several further
# enclosing-scope flags (quantized, hasTensor, hasActivation, opt, op) that
# exist only while parsing a real .tflite model file -- an external
# dependency (a real model binary plus the tflite/tensorflow packages) out
# of reach here, and out of scope for this add_isolated region regardless
# (its own g.add() calls are lines 356-391, well outside 393-411). Left as
# a no-op: it writes nothing to g, so it cannot manufacture a false match on
# either side -- both sides call the identical stub.
from rdflib import URIRef

idOfNN = "11111111-1111-1111-1111-111111111111"
neuralNetwork = URIRef(
    "https://w3id.org/tinyml-schema/neural-network-schema/neuralnetwork/" + idOfNN
)


class _FakeSubgraph:
    def OperatorsLength(self):
        return 10


graph = _FakeSubgraph()
j = 5


def addCommonInfo(layer, input_layer=False, output_layer=False):
    pass
