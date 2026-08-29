# Extracted from morph-kgc/morph-kgc@a2122e88bb : src/morph_kgc/mapping/mapping_parser.py
# region: _subject_graph_maps_to_pom (lines 191-211, stratum remove)
# licence of the source repository: see meta.json
import rdflib

def _subject_graph_maps_to_pom(mapping_graph):
    """
    Move graph maps in subject maps to the predicate object maps of subject maps.
    """

    # add the graph maps in the subject maps to every predicate object map of the subject maps
    query = 'SELECT ?sm ?gm ?pom WHERE { ' \
            f'?tm <{RML_SUBJECT_MAP}> ?sm . ' \
            f'?sm <{RML_GRAPH_MAP}> ?gm . ' \
            f'?tm <{RML_PREDICATE_OBJECT_MAP}> ?pom . }}'
    for sm, gm, pom in mapping_graph.query(query):
        mapping_graph.add((pom, rdflib.term.URIRef(RML_GRAPH_MAP), gm))

    # remove the graph maps from the subject maps
    query = 'SELECT ?sm ?gm WHERE { ' \
            f'?tm <{RML_SUBJECT_MAP}> ?sm . ' \
            f'?sm <{RML_GRAPH_MAP}> ?gm . }}'
    for sm, gm in mapping_graph.query(query):
        mapping_graph.remove((sm, rdflib.term.URIRef(RML_GRAPH_MAP), gm))

    return mapping_graph
