# Extracted from MaxBerktoldRWTH/BRICKbuilder@28f0710933 : src/ontologies/namespaces/qudt.py
# region: <module> (lines 1-40, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib.namespace import DefinedNamespace, Namespace
from rdflib import URIRef, Literal


class QUDT(DefinedNamespace):

    _NS = Namespace("http://qudt.org/schema/qudt/")

    hasQuantityKind: URIRef
    hasUnit: URIRef


class QUDTU(DefinedNamespace):

    _NS = Namespace("http://qudt.org/vocab/unit/")

    K: URIRef  # Kelvin
    M: URIRef  # Meter
    KG: URIRef  # Kilogram
    SEC: URIRef  # Second
    W: URIRef  # Watt
    KiloW: URIRef  # Kilowatt
    DEG_C: URIRef  # Degree Celsius

    _extras = [
        "KiloW-H", # Kilowatt-hour
    ]


class QUDTQK(DefinedNamespace):

    _NS = Namespace("http://qudt.org/vocab/quantitykind/")

    Temperature: URIRef
    Energy: URIRef
    Power: URIRef
    Length: URIRef
    Mass: URIRef
    Time: URIRef

