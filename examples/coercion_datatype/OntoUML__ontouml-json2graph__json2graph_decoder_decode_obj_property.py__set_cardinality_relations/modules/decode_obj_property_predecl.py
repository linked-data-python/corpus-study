# Context shim (see meta.json): determine_cardinality_bounds, copied
# verbatim from OntoUML/ontouml-json2graph@982f12b9c4
# json2graph/decoder/decode_obj_property.py, lines 194-211 -- a sibling
# function that set_cardinality_relations calls, defined earlier in the same
# source file, just outside this region's extracted line range (214-273).
# Identical for both representations.
from modules import arguments as args
from modules.cardinalities import resolve_cardinality


def determine_cardinality_bounds(
    cardinalities: str,
    property_id: str,
) -> tuple[str, str | None, str | None]:
    """Resolve a cardinality and decouple valid values into lower and upper bounds."""
    return resolve_cardinality(
        cardinalities,
        property_id,
        args.ARGUMENTS["invalid_cardinality_policy"],
    )
