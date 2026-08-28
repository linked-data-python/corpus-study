# Extracted from wordlift/worph@be7ad03789 : src/worph/core/rml_parser.py
# region: parse_rml (lines 410-476, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from .model import FnmlCall, JoinCondition, LogicalSource, MappingDocument, ObjectMapSpec, PredicateObjectMap, TermMap, TriplesMap
RML = "http://w3id.org/rml/"
RML_OLD = "http://semweb.mmlab.be/ns/rml#"
RR = "http://www.w3.org/ns/r2rml#"
DEFAULT_GRAPH = URIRef(RML + "defaultGraph")
DEFAULT_GRAPH_RR = URIRef(RR + "defaultGraph")

for pom in pom_nodes:
    graph_map_node = graph.value(pom, _u(RR, "graphMap")) or graph.value(pom, _u(RML, "graphMap"))
    if graph_map_node is not None:
        has_named_graphs = True
    graph_node = graph.value(pom, _u(RR, "graph")) or graph.value(pom, _u(RML, "graph"))
    if graph_node is not None and graph_node not in {DEFAULT_GRAPH, DEFAULT_GRAPH_RR}:
        has_named_graphs = True
    pred_maps: list[TermMap] = []
    obj_maps: list[ObjectMapSpec] = []

    pnodes = list(graph.objects(pom, _u(RR, "predicateMap")))
    pnodes += list(graph.objects(pom, _u(RML, "predicateMap")))
    pnodes += list(graph.objects(pom, _u(RML_OLD, "predicateMap")))
    for pnode in pnodes:
        pred_maps.append(_parse_term_map(graph, pnode, function_defs))

    preds = list(graph.objects(pom, _u(RR, "predicate")))
    preds += list(graph.objects(pom, _u(RML, "predicate")))
    preds += list(graph.objects(pom, _u(RML_OLD, "predicate")))
    for pred in preds:
        pred_maps.append(TermMap(constant=str(pred), term_type="iri"))

    onodes = list(graph.objects(pom, _u(RR, "objectMap")))
    onodes += list(graph.objects(pom, _u(RML, "objectMap")))
    onodes += list(graph.objects(pom, _u(RML_OLD, "objectMap")))
    for onode in onodes:
        parent_tm = graph.value(onode, _u(RR, "parentTriplesMap")) or graph.value(onode, _u(RML, "parentTriplesMap"))
        if parent_tm is not None:
            conditions: list[JoinCondition] = []
            jc_nodes = list(graph.objects(onode, _u(RR, "joinCondition")))
            jc_nodes += list(graph.objects(onode, _u(RML, "joinCondition")))
            jc_nodes += list(graph.objects(onode, _u(RML_OLD, "joinCondition")))
            for jc in jc_nodes:
                child = _first(graph, jc, [_u(RR, "child"), _u(RML, "child"), _u(RML_OLD, "child")])
                parent = _first(graph, jc, [_u(RR, "parent"), _u(RML, "parent"), _u(RML_OLD, "parent")])
                if child is not None and parent is not None:
                    conditions.append(JoinCondition(child=str(child), parent=str(parent)))
            obj_maps.append(ObjectMapSpec(parent_triples_map=str(parent_tm), join_conditions=conditions))
        elif (quoted_tm := (_first(graph, onode, [_u(RML, "quotedTriplesMap"), _u(RML_OLD, "quotedTriplesMap")]))) is not None:
            obj_maps.append(ObjectMapSpec(quoted_triples_map=str(quoted_tm)))
        else:
            obj_maps.append(ObjectMapSpec(term_map=_parse_term_map(graph, onode, function_defs)))

    objs = list(graph.objects(pom, _u(RR, "object")))
    objs += list(graph.objects(pom, _u(RML, "object")))
    objs += list(graph.objects(pom, _u(RML_OLD, "object")))
    for obj in objs:
        value = _object_value(obj)
        if isinstance(obj, URIRef):
            obj_maps.append(ObjectMapSpec(term_map=TermMap(constant=value, term_type="iri")))
            continue
        if isinstance(obj, Literal):
            obj_maps.append(
                ObjectMapSpec(
                    term_map=TermMap(
                        constant=value,
                        term_type="literal",
                        datatype=str(obj.datatype) if obj.datatype is not None else None,
                        language=obj.language,
                    )
                )
            )
            continue
        obj_maps.append(ObjectMapSpec(term_map=TermMap(constant=value, term_type="literal")))

    if pred_maps and obj_maps:
        po_maps.append(PredicateObjectMap(predicate_maps=pred_maps, object_maps=obj_maps))
