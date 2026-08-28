# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/validate_bfo_ontology.py
# region: check_inverse_of_itself (lines 1434-1451, stratum trav_single_value)
# licence of the source repository: see meta.json
def check_inverse_of_itself(g: Graph, main_properties: set[URIRef]) -> list[dict]:
    issues = []
    for prop in main_properties:
        inv = g.value(prop, OWL.inverseOf)
        if inv == prop:
            issues.append(
                {
                    "severity": "ERROR",
                    "category": "INVERSE_OF_ITSELF",
                    "subject": _short(prop, g),
                    "message": (
                        f"Property '{_label(prop, g)}' is declared as owl:inverseOf "
                        f"itself. A self-inverse property should be declared as "
                        f"owl:SymmetricProperty instead."
                    ),
                }
            )
    return issues
