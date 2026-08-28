# Extracted from comp-rob2b/kindyngen@414ebd52b2 : kindynsyn/namespaces.py
# region: <module> (lines 120-148, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib.namespace import DefinedNamespace, Namespace
from rdflib.term import URIRef

class RBDYN_COORD(DefinedNamespace):
    WrenchCoordinate: URIRef
    WrenchReference: URIRef
    InertiaReference: URIRef
    RigidBodyInertiaCoordinate: URIRef
    ForceVectorXYZ: URIRef
    TorqueVectorXYZ: URIRef
    MassScalar: URIRef
    MomentOfInertiaXYZ: URIRef
    ProductOfInertiaXYZ: URIRef
    FirstMomentOfMassVectorXYZ: URIRef

    mass: URIRef
    ixx: URIRef
    ixy: URIRef
    ixz: URIRef
    iyy: URIRef
    iyz: URIRef
    izz: URIRef

    _extras = [
        "of-wrench",
        "of-inertia",
        "as-seen-by",
        "first-moment-of-mass",
        "number-of-wrenches"            # The number of wrench instances in a wrench coordinate vector
    ]

    _NS = Namespace("https://comp-rob2b.github.io/metamodels/newtonian-rigid-body-dynamics/coordinates#")
