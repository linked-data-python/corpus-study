# Context shim (see meta.json): sibling closures and runtime state that
# addCommonInfo (the extracted region, lines 373-386) reaches as free
# variables from its enclosing scope, from Haoyu-R/How-to-Manage-TinyML-at-
# Scale@da05a79f3a (tflite2semantic_user_input.py), reproduced or stood in
# so the region executes standalone:
#
#   - addLayer, addQuantization, addTrainable, addActivation (source lines
#     292-372): four functions defined in the SAME enclosing scope as
#     addCommonInfo (all nested inside tflite2semantic's per-operator
#     loop), which addCommonInfo calls and which all close over the SAME
#     per-model graph the real code calls `g`. Bodies reproduced verbatim
#     in make_addcommoninfo_helpers(g), a factory so each side of the pair
#     gets closures bound to ITS OWN graph -- sharing one Graph instance
#     between original.py's run and translated.ldpy's run through a plain
#     module-level shim import would make the two sides silently compare
#     the very same mutated object (see meta.json).
#   - model, op, opt, interpreter: TFLite/TensorFlow objects the real code
#     builds earlier by loading an actual .tflite model file through the
#     tflite and tensorflow packages (neither installed here, and
#     unnecessary: this region only writes RDF from values those objects
#     expose, it does not itself parse a model). Minimal stand-ins exposing
#     just the methods addCommonInfo and its helpers call, returning fixed
#     codes that exist in the CODE2LAYER / CODE2ACTIVATION / CODE2DATATYPE
#     tables below.
#   - quantized, hasActivation, hasTensor, and the tensor object addTrainable
#     reads: booleans/values the real code computes while walking the
#     model's tensors (source lines 253-288); fixed here so addTrainable and
#     addActivation take the branch that writes a triple.
#
# Identical bindings for both representations.
from rdflib import Namespace

nnet = Namespace("http://tinyml-schema.org/networkschema#")


class _FakeOp:
    def OpcodeIndex(self):
        return 0


class _FakeModel:
    def OperatorCodes(self, index):
        return self

    def BuiltinCode(self):
        return 0  # -> nnet.Add in CODE2LAYER


class _FakeOpt:
    def FusedActivationFunction(self):
        return 1  # -> nnet.Relu in CODE2ACTIVATION


class _FakeInterpreter:
    def get_input_details(self):
        return [{"shape": [1, 224, 224, 3]}]

    def get_output_details(self):
        return [{"shape": [1, 1000]}]


class _FakeTensor:
    def Type(self):
        return 0  # -> nnet.Float32 in CODE2DATATYPE


model = _FakeModel()
op = _FakeOp()
opt = _FakeOpt()
interpreter = _FakeInterpreter()
quantized = True
hasActivation = True
_hasTensor = True
_tensor = _FakeTensor()


def make_addcommoninfo_helpers(g):
    """Rebuild addLayer/addQuantization/addTrainable/addActivation bound to
    the caller's own `g` (see module docstring: no shared Graph instance)."""

    def addLayer(layer, code):
        # add layer type information to each layer
        # only a few common operators are implemented
        CODE2LAYER = {
            0: nnet.Add,
            1: nnet.AvgPool2D,
            2: nnet.Concatenation,
            3: nnet.Conv2D,
            4: nnet.DepthwiseConv2D,
            6: nnet.Dequantize,
            9: nnet.FullyConnected,
            14: nnet.Logistic,
            17: nnet.MaxPool2D,
            18: nnet.Mul,
            22: nnet.Reshape,
            25: nnet.Softmax,
            28: nnet.Tanh,
            34: nnet.Pad,
            40: nnet.Mean,
            41: nnet.Sub,
            49: nnet.Split_,
            83: nnet.Pack,
            80: nnet.FakeQuant,
            88: nnet.Unpack,
            97: nnet.ResizeNearestNeighbor,
            102: nnet.SplitV,
            114: nnet.Quantize,
        }
        if code in CODE2LAYER:
            g.add((layer, nnet.hasType, CODE2LAYER[code]))
        else:
            raise ValueError("Unknown layercode %d, might be a custom layer." % code)

    def addQuantization(code):
        # Reference: https://github.com/tensorflow/tensorflow/blob/v2.1.0/tensorflow/lite/schema/schema.fbs/#L32
        CODE2DATATYPE = {
            0: nnet.Float32,
            1: nnet.Float16,
            2: nnet.Int32,
            3: nnet.Uint8,
            4: nnet.Int64,
            5: nnet.String,
            6: nnet.Bool,
            7: nnet.Int16,
            8: nnet.Complex64,
            9: nnet.Int8,
            10: nnet.Float64,
            11: nnet.Complex128,
        }
        if code in CODE2DATATYPE:
            return CODE2DATATYPE[code]
        else:
            raise ValueError("Unknown datatype code %d, might be a custom operator." % code)

    def addTrainable(layer, quantization_flag):
        # add quantization information to each layer
        # Add data type to the tensor of each node/layer
        if _hasTensor:
            g.add((layer, nnet.hasQuantization, addQuantization(_tensor.Type())))

    def addActivation(layer, code):
        # add activation information to semantic description.
        # Only a few common activation are implemented
        CODE2ACTIVATION = {
            1: nnet.Relu,
            2: nnet.Relu_n1_to_1,
            3: nnet.Relu6,
            4: nnet.Tanh,
            5: nnet.Sign_bit,
        }
        if code in CODE2ACTIVATION:
            g.add((layer, nnet.hasActivation, CODE2ACTIVATION[code]))
        else:
            print("No Activation Found for This Layer!")

    return addTrainable, addLayer, addActivation
