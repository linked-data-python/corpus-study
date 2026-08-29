# Extracted from cltl/FrameNetNLTK@96883447ff : rdf_utils.py
# region: add_decomposition (lines 192-258, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, XSD
from rdflib import URIRef

def add_decomposition(g,
                      fn_pos_to_lexinfo,
                      frame_uri,
                      lu,
                      LEMON,
                      LEXINFO,
                      DCT,
                      lemon,
                      premon,
                      le_obj):
    """
    add lemon representation of decomposition of terms

    :param rdflib.graph.Graph g: the graph to which we are added information

    :param nltk.corpus.reader.framenet.AttrDict lu: FrameNet NLTK LU object
    :param rdflib.namespace.Namespace LEMON: Lemon namespace
    :param rdflib.graph.Graph lemon: lemon graph
    :param rdflib.URIRef le_obj: uriref of LexicalEntry
    """
    # LE -> : blank node representing first :ComponentList
    assert LEMON.decomposition in lemon.subjects()

    lexeme_order_to_info = {
        lexeme['order'] : get_lexeme_info(lexeme=lexeme,
                                          premon=premon,
                                          frame_uri=frame_uri,
                                          fn_pos_to_lexinfo=fn_pos_to_lexinfo,
                                          g=g,
                                          DCT=DCT,
                                          LEMON=LEMON,
                                          LEXINFO=LEXINFO)
        for lexeme in lu.lexemes
    }

    for lexeme_order, lexeme_info in sorted(lexeme_order_to_info.items()):

        comp_uri = le_obj + f'#Component{lexeme_order}'
        comp_obj = URIRef(comp_uri)
        assert LEMON.Component in lemon.subjects()
        g.add((comp_obj, RDF.type, LEMON.Component))

        g.add((lexeme_info['bn_node'], RDF.first, comp_obj))
        if lexeme_info['le_obj_of_component'] is not None:
            assert LEMON.element in lemon.subjects()
            g.add((comp_obj, LEMON.element, lexeme_info['le_obj_of_component']))
            assert LEMON.Component in lemon.subjects()
            g.add((comp_obj, RDF.type, LEMON.Component))

        add_complement_attributes(g=g, lexeme_info=lexeme_info, comp_obj=comp_obj)

        # add relationships between :LexicalEntry and :ComponentList(s)
        order_plus_one = lexeme_order + 1

        # first :ComponentList is linked to LexicalEntry
        if lexeme_order == 1:
            g.add((le_obj, LEMON.decomposition, lexeme_info['bn_node']))
        # second: :ComponentList is linked to :ComponentList
        if order_plus_one in lexeme_order_to_info:
            g.add((lexeme_info['bn_node'],
                   RDF.rest,
                   lexeme_order_to_info[order_plus_one]['bn_node']))
        # last: last item in the list is linked to RDF.nil
        else:
            g.add((lexeme_info['bn_node'],
                  RDF.rest,
                  RDF.nil))
