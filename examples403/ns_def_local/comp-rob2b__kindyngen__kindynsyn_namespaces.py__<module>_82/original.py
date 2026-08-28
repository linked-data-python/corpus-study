# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/namespaces.py
# region: <module> (lines 82-102, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class GEOM_OP(DefinedNamespace):
    AddVelocityTwist: URIRef
    AddAccelerationTwist: URIRef
    ComposePose: URIRef
    TransformVelocityTwistToDistal: URIRef
    RotateVelocityTwistToProximalWithPose: URIRef
    TransformAccelerationTwistToDistal: URIRef

    in1: URIRef
    in2: URIRef
    composite: URIRef
    pose: URIRef
    to: URIRef                  # Transform a vector from one space _to_ another

    _extras = [
        "from",                 # Transform a vector _from_ one space to another
        "absolute-velocity",    # The _absolute velocity_ twist required for transforming an acceleration twist (the v_1 in "v_1 x v_2")
        "relative-velocity"     # The _relative velocity_ twist required for transforming an acceleration twist (the v_2 in "v_1 x v_2")
    ]

    _NS = Namespace("https://comp-rob2b.github.io/metamodels/geometry/spatial-operators#")
