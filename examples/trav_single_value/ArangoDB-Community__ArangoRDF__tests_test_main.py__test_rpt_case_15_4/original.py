# Extracted from ArangoDB-Community/ArangoRDF@48cfed903a : tests/test_main.py
# region: test_rpt_case_15_4 (lines 1672-1672, stratum trav_single_value)
# licence of the source repository: see meta.json
#
# Statement region, no visible graph (see meta.json): in the real
# test_rpt_case_15_4(name, rdf_graph), `rdf_graph` is a pytest fixture
# parameter (parsed from tests/data/rdf/cases/15_4.trig by conftest.py's
# get_rdf_graph, a ConjunctiveGraph for a .trig source), and `certainty` /
# `certainty_val_05` are local URIRef/Literal constants built a few lines
# above this statement (corpus/repos/ArangoDB-Community__ArangoRDF/tests/
# test_main.py:1660-1666). Wrapped in a function taking those three
# bindings as parameters so the region runs standalone; the statement
# itself is unchanged.

def get_mary_likes_matt_05(rdf_graph, certainty, certainty_val_05):
    mary_likes_matt_05 = rdf_graph.value(predicate=certainty, object=certainty_val_05)
    return mary_likes_matt_05
