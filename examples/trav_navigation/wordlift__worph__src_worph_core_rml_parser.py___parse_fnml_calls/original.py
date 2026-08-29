# Extracted from wordlift/worph@be7ad03789 : src/worph/core/rml_parser.py
# region: _parse_fnml_calls (lines 194-274, stratum trav_navigation)
# licence of the source repository: see meta.json
from typing import Any
from rdflib import Graph, Literal, URIRef
from .model import FnmlCall, JoinCondition, LogicalSource, MappingDocument, ObjectMapSpec, PredicateObjectMap, TermMap, TriplesMap
RML = "http://w3id.org/rml/"
RML_OLD = "http://semweb.mmlab.be/ns/rml#"
RR = "http://www.w3.org/ns/r2rml#"
FNML = "http://semweb.mmlab.be/ns/fnml#"
FNO = "https://w3id.org/function/ontology#"

def _parse_fnml_calls(graph: Graph) -> dict[str, FnmlCall]:
    calls: dict[str, FnmlCall] = {}

    p_ls = [_u(RML, "logicalSource"), _u(RML_OLD, "logicalSource")]
    p_pom = _u(RR, "predicateObjectMap")
    p_pred_map = _u(RR, "predicateMap")
    p_obj_map = _u(RR, "objectMap")
    p_constant = _u(RR, "constant")

    for subject in graph.subjects(p_pom, None):
        if _first(graph, subject, p_ls) is None:
            continue

        function_iri = None
        params: list[tuple[str, Any]] = []

        for pom in graph.objects(subject, p_pom):
            pm = graph.value(pom, p_pred_map)
            om = graph.value(pom, p_obj_map)
            if pm is None or om is None:
                continue

            pred = graph.value(pm, p_constant)
            obj_ref = graph.value(om, _u(RML, "reference")) or graph.value(om, _u(RML_OLD, "reference"))
            obj_template = graph.value(om, _u(RR, "template"))
            obj_const = graph.value(om, p_constant)
            nested = graph.value(om, _u(FNML, "functionValue"))

            if pred is None:
                continue

            pred_str = str(pred)
            if pred_str == FNO + "executes":
                function_iri = str(obj_const) if obj_const is not None else None
            else:
                if nested is not None:
                    params.append((pred_str, {"fn_ref": str(nested)}))
                elif obj_template is not None:
                    params.append((pred_str, {"template": str(obj_template)}))
                elif obj_ref is not None:
                    params.append((pred_str, {"reference": str(obj_ref)}))
                else:
                    params.append((pred_str, _object_value(obj_const)))

        if function_iri:
            calls[str(subject)] = FnmlCall(function_iri=function_iri, parameters=params)

    # Resolve nested function references recursively.
    resolved: dict[str, FnmlCall] = {}

    def resolve(key: str, stack: set[str]) -> FnmlCall:
        if key in resolved:
            return resolved[key]
        if key in stack:
            return calls[key]
        stack.add(key)
        call = calls[key]
        new_params: list[tuple[str, Any]] = []
        for name, value in call.parameters:
            if isinstance(value, dict) and "fn_ref" in value and value["fn_ref"] in calls:
                new_params.append((name, resolve(value["fn_ref"], stack)))
            else:
                new_params.append((name, value))
        stack.remove(key)
        resolved_call = FnmlCall(function_iri=call.function_iri, parameters=new_params)
        resolved[key] = resolved_call
        return resolved_call

    for key in list(calls.keys()):
        resolve(key, set())

    # Also parse direct fnml:execution nodes used in legacy mappings.
    for execution_node in set(graph.subjects(_u(FNML, "function"), None)):
        key = str(execution_node)
        if key in resolved:
            continue
        parsed = _parse_fnml_execution(graph, execution_node, resolved)
        if parsed is not None:
            resolved[key] = parsed

    return resolved
