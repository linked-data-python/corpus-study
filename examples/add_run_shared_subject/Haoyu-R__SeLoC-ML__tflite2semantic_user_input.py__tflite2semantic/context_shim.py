# Context shim (see meta.json): local bindings the enclosing tflite2semantic
# function supplies to this loop -- its own parameters (sensor_list_,
# sensor_info_) and values it computes earlier in the same function body
# (idOfNN, inputOfNN) and a nested helper it defines just above the loop
# (addHardware) -- none of which the extraction's line range (106-111)
# carries. addHardware and the input-URI construction are copied verbatim
# from Haoyu-R/SeLoC-ML@5ecc52c25e : tflite2semantic_user_input.py; idOfNN,
# sensor_info_ and sensor_list_ are illustrative call-site values of the
# right shape (a uuid4 string, a free-text sensor description, and a couple
# of the hard-coded sensor codes addHardware recognises). Identical
# bindings for both representations.
from rdflib import Namespace, URIRef

# Same value as the module-level Namespace in original.py/translated.ldpy;
# addHardware closes over its OWN copy (as it does in the source file, where
# it is a nested function reading the enclosing module's sosa_extend).
sosa_extend = Namespace("https://w3id.org/tinyml-schema/neural-network-schema/sosa_extend/")


def addHardware(code):
    # add hardware information to NN
    # only a few common sensors are implemented
    CODE2HARDWARE = {
        0: sosa_extend.Camera,
        1: sosa_extend.Microphone,
        2: sosa_extend.Accelerometer,
        3: sosa_extend.Gyroscope,
        4: sosa_extend.Thermometer,
        5: sosa_extend.OtherSensor,
    }
    return CODE2HARDWARE[code]


idOfNN = "8f14e45f-ceea-467e-bd5d-2f45f1e6a8c1"
inputOfNN = URIRef(
    "https://w3id.org/tinyml-schema/neural-network-schema/neuralnetwork/input_" + idOfNN
)
sensor_info_ = "MPU6050 accelerometer, +/-2g range"
sensor_list_ = [0, 2]
