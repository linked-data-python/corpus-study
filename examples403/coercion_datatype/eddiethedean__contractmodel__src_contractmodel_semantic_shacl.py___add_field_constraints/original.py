# Extracted from eddiethedean/contractmodel@6cccc6f3dd : src/contractmodel/semantic/shacl.py
# region: _add_field_constraints (lines 39-55, stratum coercion_datatype)
# licence of the source repository: see meta.json
from typing import Any
from contractmodel.core.ccm import CanonicalContract, ContractField

def _add_field_constraints(graph: Any, prop_uri: Any, field: ContractField) -> None:
    from rdflib import Literal
    from rdflib.namespace import SH, XSD

    if field.required and not field.nullable:
        graph.add((prop_uri, SH.minCount, Literal(1)))
    if field.constraints.min_length is not None:
        graph.add((prop_uri, SH.minLength, Literal(field.constraints.min_length)))
    if field.constraints.max_length is not None:
        graph.add((prop_uri, SH.maxLength, Literal(field.constraints.max_length)))
    if field.constraints.pattern is not None:
        graph.add((prop_uri, SH.pattern, Literal(field.constraints.pattern)))
    if field.constraints.enum_values:
        for value in field.constraints.enum_values:
            graph.add((prop_uri, SH["in"], Literal(value)))
    if field.logical_type.value == "integer":
        graph.add((prop_uri, SH.datatype, XSD.integer))
