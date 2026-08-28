# Extracted from morph-kgc/morph-kgc@a2122e88bb : test/r2rml/R2RMLTC0009b/test_R2RMLTC0009b_SQLITE.py
# region: test_R2RMLTC0009b (lines 16-25, band medium)
# licence of the source repository: see meta.json
import os
import morph_kgc
from rdflib.graph import Graph
from rdflib import compare

def test_R2RMLTC0009b():
    g = Graph()
    g.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output.nq'))

    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl')
    db_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resource.db')
    config = f'[CONFIGURATION]\ninfer_sql_datatypes=yes\noutput_format=N-QUADS\n[DataSource]\nmappings={mapping_path}\ndb_url=sqlite:///{db_path}'
    g_morph = morph_kgc.materialize(config)

    assert compare.isomorphic(g, g_morph)
