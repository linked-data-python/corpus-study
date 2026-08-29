# Extracted from pyiron/semantikon@cfd1d3ffe5 : semantikon/kg_to_flowrep.py
# region: _graph_to_function (lines 112-172, stratum trav_single_value)
# licence of the source repository: see meta.json
from typing import Any, cast
from rdflib import OWL, RDF, RDFS, Graph, Literal, URIRef, term
from rdflib.namespace import SH
from semantikon.ontology import SNS

for arg_node in graph.objects(f_node, SNS.has_part):
    if (arg_node, RDF.type, SNS.input_specification) in graph:
        target = input_args
    elif (arg_node, RDF.type, SNS.output_specification) in graph:
        target = output_args
    else:
        continue

    arg_data: dict[str, Any] = {}
    local_identifier = graph.value(arg_node, SNS.local_identifier)
    if local_identifier is not None:
        arg_data["arg"] = cast(Literal, local_identifier).toPython()
    position = graph.value(arg_node, SNS.has_parameter_position)
    if position is not None:
        arg_data["position"] = cast(Literal, position).toPython()
    default = graph.value(arg_node, SNS.has_default_literal_value)
    if default is not None:
        arg_data["default"] = cast(Literal, default).toPython()

    uri_restrictions = [
        restriction_node
        for restriction_node in graph.objects(arg_node, RDF.type)
        if (restriction_node, RDF.type, OWL.Restriction) in graph
        and (restriction_node, OWL.onProperty, SNS.is_about) in graph
        and graph.value(restriction_node, OWL.allValuesFrom) is not None
    ]
    if len(uri_restrictions) > 1:
        raise ValueError("Expected at most one URI restriction per argument.")
    if len(uri_restrictions) == 1:
        arg_data["uri"] = cast(
            URIRef, graph.value(uri_restrictions[0], OWL.allValuesFrom)
        )

    restrictions = []
    for restriction_node in graph.objects(arg_node, SNS.has_constraint):
        if (restriction_node, RDF.type, OWL.Restriction) in graph:
            pairs = tuple(
                pair
                for pair in _restriction_pairs(
                    cast(term.IdentifiedNode, restriction_node)
                )
                if pair[0] != RDF.type
            )
        elif (restriction_node, RDF.type, SH.NodeShape) in graph:
            property_shape = graph.value(restriction_node, SH.property)
            if property_shape is None:
                continue
            pairs = tuple(
                pair
                for pair in _restriction_pairs(
                    cast(term.IdentifiedNode, property_shape)
                )
                if pair[0] != RDF.type
            )
        else:
            continue
        restrictions.append(pairs)
    if len(restrictions) > 0:
        arg_data["restrictions"] = tuple(restrictions)

    target.append(arg_data)
