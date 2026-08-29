# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : starlight/parsers/turtle_parser.py
# region: _skolemize_encoding (lines 587-594, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF, XSD
from starlight.model.encoding import TT_NS, RR_NS, tt_hash, term_key, encode_dirlang_datatype

for bn in sorted_tt:
    s_n = next(g.objects(bn, RDF.subject),   None)
    p_n = next(g.objects(bn, RDF.predicate), None)
    o_n = next(g.objects(bn, RDF.object),    None)
    s_key = term_key(bn_to_uri.get(s_n, s_n))
    p_key = term_key(p_n)
    o_key = term_key(bn_to_uri.get(o_n, o_n))
    bn_to_uri[bn] = URIRef(TT_NS + tt_hash(s_key, p_key, o_key))
