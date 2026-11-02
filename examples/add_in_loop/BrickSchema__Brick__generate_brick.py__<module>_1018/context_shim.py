# Context shim (see meta.json): what generate_brick.py has in scope at line
# 1018, so the region executes outside the Brick repository.
#
#   * the bricksrc.namespaces constants (verbatim values from
#     BrickSchema/Brick@c12949f236 bricksrc/namespaces.py);
#   * a stand-in for the top-level `brickschema` module (the extraction kept
#     `G = brickschema.Graph()` but not `import brickschema`).  The real
#     brickschema.Graph is an rdflib Graph that binds the Brick prefixes and
#     adds ontology-loading and SHACL machinery this region never calls.
#     Here it is an rdflib Graph that binds the same prefixes AND already
#     holds what the earlier passes of generate_brick.py had added to the
#     module graph G by line 1018: the Brick quantities and their QUDT
#     references (a small slice, with neighbours that must not be read);
#   * stand-ins for `get_units` (bricksrc/quantities.py, which looks the
#     units of a QUDT quantity kind up) and `get_units_brick` (defined in
#     generate_brick.py, which yields the (unit, symbol, label) triples of a
#     Brick quantity), reduced to lookup tables over the same slice.
#
# Identical bindings for both representations.
from rdflib import Graph, Namespace, URIRef

BRICK = Namespace("https://brickschema.org/schema/Brick#")
TAG = Namespace("https://brickschema.org/schema/BrickTag#")
BSH = Namespace("https://brickschema.org/schema/BrickShape#")
REF = Namespace("https://brickschema.org/schema/Brick/ref#")
SH = Namespace("http://www.w3.org/ns/shacl#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
REC = Namespace("https://w3id.org/rec#")
QUDT = Namespace("http://qudt.org/schema/qudt/")

QUDTQK = Namespace("http://qudt.org/vocab/quantitykind/")
UNIT = Namespace("http://qudt.org/vocab/unit/")

_SO_FAR = """
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix qudt: <http://qudt.org/schema/qudt/> .
@prefix qk: <http://qudt.org/vocab/quantitykind/> .
@prefix unit: <http://qudt.org/vocab/unit/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# quantities with a QUDT reference (the region reads these)
brick:Temperature a brick:Quantity ; brick:hasQUDTReference qk:Temperature .
brick:Length      a brick:Quantity ; brick:hasQUDTReference qk:Length .
brick:Thickness   a brick:Quantity ; brick:hasQUDTReference qk:Length .
brick:Luminosity  a brick:Quantity ; brick:hasQUDTReference qk:LuminousFlux .
# a quantity with units already attached
brick:Power       a brick:Quantity ; brick:hasQUDTReference qk:Power ;
                  qudt:applicableUnit unit:W .

# neighbours that must not be read
brick:Humidity    a brick:Quantity .                                  # no reference
brick:Pressure    brick:hasQUDTReference qk:Pressure .                # not typed
brick:Sensor      a brick:Class ; brick:hasQUDTReference qk:Length .  # another type
unit:K            a qudt:Unit .
"""


class _BrickschemaGraph(Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for prefix, ns in (("brick", BRICK), ("tag", TAG), ("bsh", BSH),
                           ("ref", REF), ("sh", SH), ("owl", OWL),
                           ("rdf", RDF), ("rdfs", RDFS), ("skos", SKOS),
                           ("sosa", SOSA), ("vcard", VCARD), ("rec", REC),
                           ("qudt", QUDT)):
            self.bind(prefix, ns)
        self.parse(data=_SO_FAR, format="turtle")


class _Brickschema:
    Graph = _BrickschemaGraph


brickschema = _Brickschema()

quantity_definitions = {}

_UNITS_OF_QUDT_QUANTITY = {
    QUDTQK.Temperature: [UNIT.DEG_C, UNIT.K],
    QUDTQK.Length: [UNIT.M, UNIT.KiloM],
    QUDTQK.Power: [UNIT.W, UNIT.KiloW],
}

_UNITS_OF_BRICK_QUANTITY = {
    BRICK.Temperature: [(UNIT.DEG_F, "°F", "degree Fahrenheit")],
    BRICK.Thickness: [(UNIT.MilliM, "mm", "millimetre"),
                      (UNIT.IN, "in", "inch")],
}


def get_units(qudt_quant):
    return list(_UNITS_OF_QUDT_QUANTITY.get(qudt_quant, []))


def get_units_brick(brick_quant):
    return list(_UNITS_OF_BRICK_QUANTITY.get(brick_quant, []))
