# Extracted from morph-kgc/morph-kgc@a2122e88bb : src/morph_kgc/mapping/yarrrml.py
# region: _translate_yarrrml_to_rml (lines 584-700, stratum add_in_loop)
# licence of the source repository: see meta.json
import rdflib
from shim import (
    RDF_TYPE,
    RML_LOGICAL_SOURCE, RML_SUBJECT_MAP, RML_QUOTED_TRIPLES_MAP,
    RML_NON_ASSERTED_TRIPLES_MAP_CLASS, RML_JOIN_CONDITION, RML_CHILD,
    RML_PARENT, RML_TERM_TYPE, RML_IRI, RML_BLANK_NODE, RML_GRAPH_MAP,
    RML_PREDICATE_OBJECT_MAP, RML_PREDICATE_MAP, RML_OBJECT_MAP,
    RML_PARENT_TRIPLES_MAP, RML_LANGUAGE_SHORTCUT, RML_DATATYPE_SHORTCUT,
    RML_LITERAL, RML_CONSTANT,
    _add_source, _add_template, _translate_yarrrml_function_to_rml,
)

term_types = {'iri': RML_IRI, 'literal': RML_LITERAL, 'blanknode': RML_BLANK_NODE}


def _add_quoted(mapping_graph, term_map_bnode, term_map):
    quoted = 'quoted' if 'quoted' in term_map else 'quotedNonAsserted'
    for ref_tm in tm_id_to_norm_tm_ids[term_map[quoted]]:
        mapping_graph.add((term_map_bnode, rdflib.URIRef(RML_QUOTED_TRIPLES_MAP), rdflib.URIRef(ref_tm)))
        if quoted == 'quotedNonAsserted':
            # only non asserted triples maps are typed
            mapping_graph.add((rdflib.URIRef(ref_tm), rdflib.URIRef(RDF_TYPE), rdflib.URIRef(RML_NON_ASSERTED_TRIPLES_MAP_CLASS)))


def _add_join_condition(mapping_graph, term_map_bnode, condition):
    join_condition_bnode = rdflib.BNode()
    mapping_graph.add((term_map_bnode, rdflib.URIRef(RML_JOIN_CONDITION), join_condition_bnode))
    for parameter in condition['parameters']:
        if parameter[0] == 'str1':
            mapping_graph.add((join_condition_bnode, rdflib.URIRef(RML_CHILD), rdflib.Literal(parameter[1][2:-1])))
        elif parameter[0] == 'str2':
            mapping_graph.add((join_condition_bnode, rdflib.URIRef(RML_PARENT), rdflib.Literal(parameter[1][2:-1])))


for mapping_id, mapping_value in yarrrml_mapping['mappings'].items():
    triples_map_iri = rdflib.URIRef(mapping_id)

    ####################### SOURCES #####################
    source_bnode = rdflib.BNode()
    mapping_graph.add((triples_map_iri, rdflib.URIRef(RML_LOGICAL_SOURCE), source_bnode))
    mapping_graph = _add_source(mapping_graph, mapping_value['sources'], source_bnode)

    ####################### SUBJECTS ####################
    subject_bnode = rdflib.BNode()
    mapping_graph.add((triples_map_iri, rdflib.URIRef(RML_SUBJECT_MAP), subject_bnode))
    subjects = mapping_value.get('subjects')
    if type(subjects) is str:
        subjects = {'value': subjects}
    if 'subjects' not in mapping_value:
        # it is a blank node
        mapping_graph += [(subject_bnode, rdflib.URIRef(RML_CONSTANT), rdflib.BNode()),
                          (subject_bnode, rdflib.URIRef(RML_TERM_TYPE), rdflib.URIRef(RML_BLANK_NODE))]
    elif type(subjects) is dict:
        # it is quoted
        if 'quoted' in subjects or 'quotedNonAsserted' in subjects:
            _add_quoted(mapping_graph, subject_bnode, subjects)
        elif 'function' in subjects:
            mapping_graph = _translate_yarrrml_function_to_rml(mapping_graph, subjects, subject_bnode)
        else:
            mapping_graph = _add_template(mapping_graph, subject_bnode, subjects['value'])

        if 'condition' in subjects:
            _add_join_condition(mapping_graph, subject_bnode, subjects['condition'])
        if 'type' in subjects:
            if subjects['type'] not in ('iri', 'blanknode'):
                raise ValueError(f"Found an invalid termtype `{subjects['type']}` in YARRRML mapping.")
            mapping_graph.add((subject_bnode, rdflib.URIRef(RML_TERM_TYPE), rdflib.URIRef(term_types[subjects['type']])))

    ####################### GRAPHS ####################
    if 'graphs' in mapping_value:
        graph_bnode = rdflib.BNode()
        mapping_graph.add((triples_map_iri, rdflib.URIRef(RML_GRAPH_MAP), graph_bnode))
        mapping_graph = _add_template(mapping_graph, graph_bnode, mapping_value['graphs'])

    ####################### PREDICATE OBJECTS ############
    if 'predicateobjects' in mapping_value:
        predicateobject_bnode = rdflib.BNode()
        mapping_graph.add((triples_map_iri, rdflib.URIRef(RML_PREDICATE_OBJECT_MAP), predicateobject_bnode))

        for position, property in zip(['predicates', 'objects', 'graphs'], [RML_PREDICATE_MAP, RML_OBJECT_MAP, RML_GRAPH_MAP]):
            if position in mapping_value['predicateobjects']:
                term_map = mapping_value['predicateobjects'][position]
                if type(term_map) is str:
                    term_map = {'value': term_map}
                if type(term_map) is dict:
                    term_map_bnode = rdflib.BNode()
                    if 'mappings' in term_map and 'function' not in term_map:
                        # referencing object map

                        # just a single normalized triples map is needed (only the subject map is used)
                        ref_tm = list(tm_id_to_norm_tm_ids[term_map['mappings']])[0]

                        mapping_graph += [(predicateobject_bnode, rdflib.URIRef(property), term_map_bnode),
                                          (term_map_bnode, rdflib.URIRef(RML_PARENT_TRIPLES_MAP), rdflib.URIRef(ref_tm))]
                    else:
                        mapping_graph.add((predicateobject_bnode, rdflib.URIRef(property), term_map_bnode))
                        if 'function' in term_map:
                            mapping_graph = _translate_yarrrml_function_to_rml(mapping_graph, term_map, term_map_bnode)
                        elif 'quoted' in term_map or 'quotedNonAsserted' in term_map:
                            _add_quoted(mapping_graph, term_map_bnode, term_map)
                        else:
                            # object dict
                            mapping_graph = _add_template(mapping_graph, term_map_bnode, term_map['value'])

                    if 'condition' in term_map:
                        _add_join_condition(mapping_graph, term_map_bnode, term_map['condition'])
                    if 'language' in term_map:
                        mapping_graph.add((term_map_bnode, rdflib.URIRef(RML_LANGUAGE_SHORTCUT), rdflib.Literal(term_map['language'])))
                    elif 'datatype' in term_map:
                        mapping_graph.add((term_map_bnode, rdflib.URIRef(RML_DATATYPE_SHORTCUT), rdflib.URIRef(term_map['datatype'])))
                    elif 'type' in term_map:
                        if term_map['type'] not in ('iri', 'literal', 'blanknode'):
                            raise ValueError(f"Found an invalid termtype `{term_map['type']}` in YARRRML mapping.")
                        mapping_graph.add((term_map_bnode, rdflib.URIRef(RML_TERM_TYPE), rdflib.URIRef(term_types[term_map['type']])))
