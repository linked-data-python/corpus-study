# Extracted from morph-kgc/morph-kgc@a2122e88bb : src/morph_kgc/mapping/yarrrml.py
# region: _translate_yarrrml_function_to_rml (lines 511-553, stratum add_isolated)
# licence of the source repository: see meta.json
import rdflib

def _translate_yarrrml_function_to_rml(mapping_graph, function, term_map):
    execution_bnode = rdflib.term.BNode()
    mapping_graph.add((term_map, rdflib.term.URIRef(RML_EXECUTION), execution_bnode))

    if 'datatype' in function:
        mapping_graph.add((term_map, rdflib.term.URIRef(RML_DATATYPE_SHORTCUT), rdflib.term.URIRef(function['datatype'])))
    elif 'language' in function:
        mapping_graph.add((term_map, rdflib.term.URIRef(RML_LANGUAGE_SHORTCUT), rdflib.term.URIRef(function['language'])))
    elif 'type' in function:
        if function['type'] == 'iri':
            mapping_graph.add((term_map, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_IRI)))
        elif function['type'] == 'literal':
            mapping_graph.add((term_map, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_LITERAL)))
        elif function['type'] == 'blanknode':
            mapping_graph.add((term_map, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_BLANK_NODE)))
        else:
            raise ValueError(f"Found an invalid termtype `{function['type']}` in YARRRML mapping.")

    function_bnode = rdflib.term.BNode()
    mapping_graph.add((execution_bnode, rdflib.term.URIRef(RML_FUNCTION_MAP), function_bnode))
    mapping_graph.add((function_bnode, rdflib.term.URIRef(RML_CONSTANT), rdflib.term.URIRef(function['function'])))

    if 'parameters' in function:
        # TODO: deal with recursivity
        for i, parameter in enumerate(function['parameters']):
            input_bnode = rdflib.term.BNode()
            mapping_graph.add((execution_bnode, rdflib.term.URIRef(RML_INPUT), input_bnode))

            parameter_bnode = rdflib.term.BNode()
            mapping_graph.add((input_bnode, rdflib.term.URIRef(RML_PARAMETER_MAP), parameter_bnode))

            value_bnode = rdflib.term.BNode()
            mapping_graph.add((input_bnode, rdflib.term.URIRef(RML_VALUE_MAP), value_bnode))

            if type(parameter['value']) is dict and 'function' in parameter['value']:
                # composite function
                mapping_graph.add((parameter_bnode, rdflib.term.URIRef(RML_CONSTANT), rdflib.term.URIRef(parameter['parameter'])))
                mapping_graph = _translate_yarrrml_function_to_rml(mapping_graph, parameter['value'], value_bnode)
            else:
                mapping_graph.add((parameter_bnode, rdflib.term.URIRef(RML_CONSTANT), rdflib.term.URIRef(parameter['parameter'])))
                mapping_graph = _add_template(mapping_graph, value_bnode, parameter['value'])

    return mapping_graph
