# Extracted from morph-kgc/morph-kgc@a2122e88bb : src/morph_kgc/mapping/yarrrml.py
# region: _translate_yarrrml_to_rml (lines 584-700, stratum add_in_loop)
# licence of the source repository: see meta.json
import rdflib

for mapping_id, mapping_value in yarrrml_mapping['mappings'].items():
    triples_map_iri = rdflib.term.URIRef(mapping_id)

    ####################### SOURCES #####################
    source_bnode = rdflib.BNode()
    mapping_graph.add((triples_map_iri, rdflib.term.URIRef(RML_LOGICAL_SOURCE), source_bnode))
    mapping_graph = _add_source(mapping_graph, mapping_value['sources'], source_bnode)

    ####################### SUBJECTS ####################
    if 'subjects' in mapping_value:
        subject_bnode = rdflib.BNode()
        mapping_graph.add((triples_map_iri, rdflib.term.URIRef(RML_SUBJECT_MAP), subject_bnode))
        if type(mapping_value['subjects']) is str:
            mapping_graph = _add_template(mapping_graph, subject_bnode, mapping_value['subjects'])
        elif type(mapping_value['subjects']) is dict:
            # it is quoted
            if 'quoted' in mapping_value['subjects']:
                for ref_tm in tm_id_to_norm_tm_ids[mapping_value['subjects']['quoted']]:
                    mapping_graph.add((subject_bnode, rdflib.term.URIRef(RML_QUOTED_TRIPLES_MAP), rdflib.term.URIRef(ref_tm)))
            elif 'quotedNonAsserted' in mapping_value['subjects']:
                # only non asserted triples maps are typed
                for ref_tm in tm_id_to_norm_tm_ids[mapping_value['subjects']['quotedNonAsserted']]:
                    mapping_graph.add((subject_bnode, rdflib.term.URIRef(RML_QUOTED_TRIPLES_MAP), rdflib.term.URIRef(ref_tm)))
                    mapping_graph.add((rdflib.term.URIRef(ref_tm), rdflib.term.URIRef(RDF_TYPE), rdflib.term.URIRef(RML_NON_ASSERTED_TRIPLES_MAP_CLASS)))
            elif 'function' in mapping_value['subjects']:
                mapping_graph = _translate_yarrrml_function_to_rml(mapping_graph, mapping_value['subjects'], subject_bnode)
            else:
                mapping_graph = _add_template(mapping_graph, subject_bnode, mapping_value['subjects']['value'])

            if 'condition' in mapping_value['subjects']:
                join_condition_bnode = rdflib.BNode()
                mapping_graph.add((subject_bnode, rdflib.term.URIRef(RML_JOIN_CONDITION), join_condition_bnode))
                for parameter in mapping_value['subjects']['condition']['parameters']:
                    if parameter[0] == 'str1':
                        mapping_graph.add((join_condition_bnode, rdflib.term.URIRef(RML_CHILD), rdflib.term.Literal(parameter[1][2:-1])))
                    elif parameter[0] == 'str2':
                        mapping_graph.add((join_condition_bnode, rdflib.term.URIRef(RML_PARENT), rdflib.term.Literal(parameter[1][2:-1])))
            if 'type' in mapping_value['subjects']:
                if mapping_value['subjects']['type'] == 'iri':
                    mapping_graph.add((subject_bnode, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_IRI)))
                elif mapping_value['subjects']['type'] == 'blanknode':
                    mapping_graph.add((subject_bnode, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_BLANK_NODE)))
                else:
                    raise ValueError(f"Found an invalid termtype `{mapping_value['subjects']['type']}` in YARRRML mapping.")
    else:
        # it is a blank node
        subject_bnode = rdflib.BNode()
        mapping_graph.add((triples_map_iri, rdflib.term.URIRef(RML_SUBJECT_MAP), subject_bnode))
        mapping_graph.add((subject_bnode, rdflib.term.URIRef(RML_CONSTANT), rdflib.BNode()))
        mapping_graph.add((subject_bnode, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_BLANK_NODE)))

    ####################### GRAPHS ####################
    if 'graphs' in mapping_value:
        graph_bnode = rdflib.BNode()
        mapping_graph.add((triples_map_iri, rdflib.term.URIRef(RML_GRAPH_MAP), graph_bnode))
        mapping_graph = _add_template(mapping_graph, graph_bnode, mapping_value['graphs'])

    ####################### PREDICATE OBJECTS ############
    if 'predicateobjects' in mapping_value:
        predicateobject_bnode = rdflib.BNode()
        mapping_graph.add((triples_map_iri, rdflib.term.URIRef(RML_PREDICATE_OBJECT_MAP), predicateobject_bnode))

        for position, property in zip(['predicates', 'objects', 'graphs'], [RML_PREDICATE_MAP, RML_OBJECT_MAP, RML_GRAPH_MAP]):
            if position in mapping_value['predicateobjects']:
                term_map_bnode = rdflib.BNode()
                if type(mapping_value['predicateobjects'][position]) is str:
                    # template
                    mapping_graph.add((predicateobject_bnode, rdflib.term.URIRef(property), term_map_bnode))
                    mapping_graph = _add_template(mapping_graph, term_map_bnode, mapping_value['predicateobjects'][position])
                elif type(mapping_value['predicateobjects'][position]) is dict:
                    if 'function' in mapping_value['predicateobjects'][position]:
                        mapping_graph.add((predicateobject_bnode, rdflib.term.URIRef(property), term_map_bnode))
                        mapping_graph = _translate_yarrrml_function_to_rml(mapping_graph, mapping_value['predicateobjects'][position], term_map_bnode)
                    elif 'mappings' in mapping_value['predicateobjects'][position]:
                        # referencing object map

                        # just a single normalized triples map is needed (only the subject map is used)
                        ref_tm = list(tm_id_to_norm_tm_ids[mapping_value['predicateobjects'][position]['mappings']])[0]

                        mapping_graph.add((predicateobject_bnode, rdflib.term.URIRef(property), term_map_bnode))
                        mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_PARENT_TRIPLES_MAP), rdflib.term.URIRef(ref_tm)))
                    elif 'quoted' in mapping_value['predicateobjects'][position] or 'quotedNonAsserted' in mapping_value['predicateobjects'][position]:
                        mapping_graph.add((predicateobject_bnode, rdflib.term.URIRef(property), term_map_bnode))
                        if 'quoted' in mapping_value['predicateobjects'][position]:
                            for ref_tm in tm_id_to_norm_tm_ids[mapping_value['predicateobjects'][position]['quoted']]:
                                mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_QUOTED_TRIPLES_MAP), rdflib.term.URIRef(ref_tm)))
                        elif 'quotedNonAsserted' in mapping_value['predicateobjects'][position]:
                            # only non asserted triples maps are typed
                            for ref_tm in tm_id_to_norm_tm_ids[mapping_value['predicateobjects'][position]['quotedNonAsserted']]:
                                mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_QUOTED_TRIPLES_MAP), rdflib.term.URIRef(ref_tm)))
                                mapping_graph.add((rdflib.term.URIRef(ref_tm), rdflib.term.URIRef(RDF_TYPE), rdflib.term.URIRef(RML_NON_ASSERTED_TRIPLES_MAP_CLASS)))
                    else:
                        # object dict
                        mapping_graph.add((predicateobject_bnode, rdflib.term.URIRef(property), term_map_bnode))
                        mapping_graph = _add_template(mapping_graph, term_map_bnode, mapping_value['predicateobjects'][position]['value'])

                    if 'condition' in mapping_value['predicateobjects'][position]:
                        join_condition_bnode = rdflib.BNode()
                        mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_JOIN_CONDITION), join_condition_bnode))
                        for parameter in mapping_value['predicateobjects'][position]['condition']['parameters']:
                            if parameter[0] == 'str1':
                                mapping_graph.add((join_condition_bnode, rdflib.term.URIRef(RML_CHILD), rdflib.term.Literal(parameter[1][2:-1])))
                            elif parameter[0] == 'str2':
                                mapping_graph.add((join_condition_bnode, rdflib.term.URIRef(RML_PARENT), rdflib.term.Literal(parameter[1][2:-1])))
                    if 'language' in mapping_value['predicateobjects'][position]:
                        mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_LANGUAGE_SHORTCUT), rdflib.term.Literal(mapping_value['predicateobjects'][position]['language'])))
                    elif 'datatype' in mapping_value['predicateobjects'][position]:
                        mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_DATATYPE_SHORTCUT), rdflib.term.URIRef(mapping_value['predicateobjects'][position]['datatype'])))
                    elif 'type' in mapping_value['predicateobjects'][position]:
                        if mapping_value['predicateobjects'][position]['type'] == 'iri':
                            mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_IRI)))
                        elif mapping_value['predicateobjects'][position]['type'] == 'literal':
                            mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_LITERAL)))
                        elif mapping_value['predicateobjects'][position]['type'] == 'blanknode':
                            mapping_graph.add((term_map_bnode, rdflib.term.URIRef(RML_TERM_TYPE), rdflib.term.URIRef(RML_BLANK_NODE)))
                        else:
                            raise ValueError(f"Found an invalid termtype `{mapping_value['predicateobjects'][position]['type']}` in YARRRML mapping.")
