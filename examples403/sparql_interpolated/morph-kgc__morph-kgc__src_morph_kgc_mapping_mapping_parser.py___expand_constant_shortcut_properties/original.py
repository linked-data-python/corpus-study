# Extracted from morph-kgc/morph-kgc@a2122e88bb : src/morph_kgc/mapping/mapping_parser.py
# region: _expand_constant_shortcut_properties (lines 142-169, stratum sparql_interpolated)
# licence of the source repository: see meta.json
import rdflib

def _expand_constant_shortcut_properties(mapping_graph):
    """
    Expand constant shortcut properties.
    See R2RML specification (https://www.w3.org/2001/sw/rdb2rdf/r2rml/#constant).
    """

    constant_shortcuts_dict = {
        RML_SUBJECT_SHORTCUT: RML_SUBJECT_MAP,
        RML_PREDICATE_SHORTCUT: RML_PREDICATE_MAP,
        RML_OBJECT_SHORTCUT: RML_OBJECT_MAP,
        RML_LANGUAGE_SHORTCUT: RML_LANGUAGE_MAP,
        RML_DATATYPE_SHORTCUT: RML_DATATYPE_MAP,
        RML_GRAPH_SHORTCUT: RML_GRAPH_MAP,
        RML_FUNCTION_SHORTCUT: RML_FUNCTION_MAP,
        RML_RETURN_SHORTCUT: RML_RETURN_MAP,
        RML_PARAMETER_SHORTCUT: RML_PARAMETER_MAP,
        RML_VALUE_SHORTCUT: RML_VALUE_MAP
    }

    for constant_shortcut, constant_property in constant_shortcuts_dict.items():
        for s, o in mapping_graph.query(f'SELECT ?s ?o WHERE {{?s <{constant_shortcut}> ?o .}}'):
            blanknode = rdflib.BNode()
            mapping_graph.add((s, rdflib.term.URIRef(constant_property), blanknode))
            mapping_graph.add((blanknode, rdflib.term.URIRef(RML_CONSTANT), o))

        mapping_graph.remove((None, rdflib.term.URIRef(constant_shortcut), None))

    return mapping_graph
