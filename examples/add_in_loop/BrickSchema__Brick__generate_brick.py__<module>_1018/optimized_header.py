# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: <module> (lines 1018-1024, stratum add_in_loop)
# licence of the source repository: see meta.json
from context_shim import QUDT, brickschema, get_units, get_units_brick
G = brickschema.Graph()
for brick_quant, qudt_quant in G.query("""SELECT ?quantity ?qudtquant WHERE {
        ?quantity a brick:Quantity ; brick:hasQUDTReference ?qudtquant }"""):
    G += [(brick_quant, QUDT.applicableUnit, unit) for unit in get_units(qudt_quant)]
    # the symbols, units, and labels are already defined in the previous pass
    G += [(brick_quant, QUDT.applicableUnit, unit) for unit, _, _ in get_units_brick(brick_quant)]
