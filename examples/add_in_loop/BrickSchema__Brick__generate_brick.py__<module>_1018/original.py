# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: <module> (lines 1018-1024, stratum add_in_loop)
# licence of the source repository: see meta.json
import brickschema
from bricksrc.namespaces import (
    BRICK,
    BSH,
    REC,
    RDF,
    OWL,
    RDFS,
    TAG,
    SOSA,
    SKOS,
    QUDT,
    VCARD,
    SH,
    REF,
)
from bricksrc.quantities import quantity_definitions, get_units
G = brickschema.Graph()
res = G.query(
    """SELECT ?quantity ?qudtquant WHERE {
                ?quantity rdf:type brick:Quantity .
                ?quantity brick:hasQUDTReference ?qudtquant
                }"""
)

for r in res:
    brick_quant, qudt_quant = r
    for unit in get_units(qudt_quant):
        G.add((brick_quant, QUDT.applicableUnit, unit))
    # the symbols, units, and labels are already defined in the previous pass
    for unit, symb, label in get_units_brick(brick_quant):
        G.add((brick_quant, QUDT.applicableUnit, unit))
