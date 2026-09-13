# Context shim (see meta.json): the RML_* IRI constants (subset used by this
# region) from morph_kgc/constants.py, and the verbatim helper functions
# _template_to_rml / _add_source / _add_template / _translate_yarrrml_function_to_rml
# from morph_kgc/mapping/yarrrml.py, both from morph-kgc/morph-kgc@a2122e88bb,
# so the region executes outside the package. Identical bindings for both
# representations.
import rdflib

RDF_NAMESPACE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
RDF_TYPE = f'{RDF_NAMESPACE}type'

RML_NAMESPACE = 'http://w3id.org/rml/'
RML_LOGICAL_SOURCE = f'{RML_NAMESPACE}logicalSource'
RML_SOURCE = f'{RML_NAMESPACE}source'
RML_QUERY = f'{RML_NAMESPACE}query'
RML_ITERATOR = f'{RML_NAMESPACE}iterator'
RML_REFERENCE = f'{RML_NAMESPACE}reference'
RML_REFERENCE_FORMULATION = f'{RML_NAMESPACE}referenceFormulation'
RML_TABLE_NAME = f'{RML_NAMESPACE}tableName'
RML_PARENT_TRIPLES_MAP = f'{RML_NAMESPACE}parentTriplesMap'
RML_SUBJECT_MAP = f'{RML_NAMESPACE}subjectMap'
RML_PREDICATE_MAP = f'{RML_NAMESPACE}predicateMap'
RML_OBJECT_MAP = f'{RML_NAMESPACE}objectMap'
RML_GRAPH_MAP = f'{RML_NAMESPACE}graphMap'
RML_DATATYPE_SHORTCUT = f'{RML_NAMESPACE}datatype'
RML_LANGUAGE_SHORTCUT = f'{RML_NAMESPACE}language'
RML_PREDICATE_OBJECT_MAP = f'{RML_NAMESPACE}predicateObjectMap'
RML_CONSTANT = f'{RML_NAMESPACE}constant'
RML_TEMPLATE = f'{RML_NAMESPACE}template'
RML_CHILD = f'{RML_NAMESPACE}child'
RML_PARENT = f'{RML_NAMESPACE}parent'
RML_JOIN_CONDITION = f'{RML_NAMESPACE}joinCondition'
RML_TERM_TYPE = f'{RML_NAMESPACE}termType'
RML_IRI = f'{RML_NAMESPACE}IRI'
RML_LITERAL = f'{RML_NAMESPACE}Literal'
RML_BLANK_NODE = f'{RML_NAMESPACE}BlankNode'
RML_NON_ASSERTED_TRIPLES_MAP_CLASS = f'{RML_NAMESPACE}NonAssertedTriplesMap'
RML_QUOTED_TRIPLES_MAP = f'{RML_NAMESPACE}quotedTriplesMap'
RML_EXECUTION = f'{RML_NAMESPACE}functionExecution'
RML_FUNCTION_MAP = f'{RML_NAMESPACE}functionMap'
RML_INPUT = f'{RML_NAMESPACE}input'
RML_PARAMETER_MAP = f'{RML_NAMESPACE}parameterMap'
RML_VALUE_MAP = f'{RML_NAMESPACE}valueMap'
RML_CSV = f'{RML_NAMESPACE}CSV'

REFERENCE_FORMULATION_DICT = {
    'csv': RML_CSV,
}


def _template_to_rml(yarrrml_template):
    rml_template = ''

    ref_ini_pos = yarrrml_template.find('$(')
    while ref_ini_pos != -1:
        rml_template += f'{yarrrml_template[:ref_ini_pos]}{{'
        yarrrml_template = f'{yarrrml_template[ref_ini_pos+2:]}'

        ref_end_pos = yarrrml_template.find(')')
        rml_template += f'{yarrrml_template[:ref_end_pos]}}}'
        yarrrml_template = yarrrml_template[ref_end_pos+1:]

        ref_ini_pos = yarrrml_template.find('$(')

    # final constant string
    rml_template += yarrrml_template

    return rml_template


def _add_source(mapping_graph, source, source_bnode):
    if 'access' in source:
        mapping_graph.add((source_bnode, rdflib.term.URIRef(RML_SOURCE), rdflib.term.Literal(source['access'])))
    if 'query' in source:
        mapping_graph.add((source_bnode, rdflib.term.URIRef(RML_QUERY), rdflib.term.Literal(source['query'])))
    if 'table' in source:
        mapping_graph.add((source_bnode, rdflib.term.URIRef(RML_TABLE_NAME), rdflib.term.Literal(source['table'])))
    if 'iterator' in source:
        mapping_graph.add((source_bnode, rdflib.term.URIRef(RML_ITERATOR), rdflib.term.Literal(source['iterator'])))
    if 'referenceFormulation' in source:
        mapping_graph.add((source_bnode, rdflib.term.URIRef(RML_REFERENCE_FORMULATION),
                           rdflib.term.Literal(REFERENCE_FORMULATION_DICT[source['referenceFormulation'].lower()])))

    return mapping_graph


def _add_template(mapping_graph, term_map_bnode, yarrrml_template):
    yarrrml_template = str(yarrrml_template)
    if yarrrml_template.startswith('$(') and yarrrml_template.count('$(') == 1:
        # a YARRRML template may be composed of simply one reference
        # in that case the YARRRML template corresponds to an RML reference
        mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_REFERENCE), rdflib.term.Literal(yarrrml_template[2:-1])))
    elif '$(' in yarrrml_template:
        rml_template = _template_to_rml(yarrrml_template)
        mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_TEMPLATE), rdflib.term.Literal(rml_template)))
    elif 'a' == yarrrml_template:
        mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_CONSTANT), rdflib.term.URIRef(RDF_TYPE)))
    else:
        # a YARRRML template may have 0 references
        # in that case the YARRRML template corresponds to an RML constant
        if yarrrml_template.startswith('http') or yarrrml_template.startswith('ftp'):
            mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_CONSTANT), rdflib.term.URIRef(yarrrml_template)))
        else:
            mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_CONSTANT), rdflib.term.Literal(yarrrml_template)))

    return mapping_graph


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


def make_fixture():
    """Fixture YARRRML mapping exercising every branch of the region: a
    reference-only subject template, a quoted subject with a join condition
    and an explicit term type, a function-valued subject, and a mapping with
    no 'subjects' key at all (implicit blank node); predicate-object maps
    covering a template, a referencing object map, a quotedNonAsserted
    object with a language tag, a function-valued predicate, and an explicit
    object term type.
    """
    yarrrml_mapping = {
        'mappings': {
            'tm1': {
                'sources': {'access': 'data.csv', 'table': 'mytable',
                            'iterator': 'row', 'referenceFormulation': 'csv'},
                'subjects': '$(id)',
                'graphs': 'http://ex.org/g1',
                'predicateobjects': {'predicates': 'http://ex.org/p1',
                                      'objects': '$(val)'},
            },
            'tm2': {
                'sources': {'query': 'SELECT * FROM t'},
                'subjects': {
                    'quoted': 'tm1',
                    'condition': {'parameters': [('str1', '$(a)'), ('str2', '$(b)')]},
                    'type': 'iri',
                },
                'predicateobjects': {
                    'objects': {'mappings': 'tm1'},
                    'graphs': {'quotedNonAsserted': 'tm1', 'language': 'en'},
                },
            },
            'tm3': {
                'sources': {'access': 'data2.csv'},
                'subjects': {
                    'function': 'someFn',
                    'parameters': [{'parameter': 'p1', 'value': '$(x)'}],
                },
                'predicateobjects': {
                    'predicates': {'value': 'http://ex.org/p3',
                                   'datatype': 'http://www.w3.org/2001/XMLSchema#string'},
                },
            },
            'tm4': {
                'sources': {'iterator': 'x'},
                'predicateobjects': {
                    'objects': {'value': 'http://ex.org/p4', 'type': 'blanknode'},
                },
            },
        },
    }
    tm_id_to_norm_tm_ids = {'tm1': {'tm1'}, 'tm2': {'tm2'}, 'tm3': {'tm3'}, 'tm4': {'tm4'}}
    return yarrrml_mapping, tm_id_to_norm_tm_ids
