# Extracted from morph-kgc/morph-kgc@a2122e88bb : test/rml-in-memory/json_dictionary/RMLIMTC0000/test_RMLTC0000_DICT.py
# region: test_RMLTC0000 (lines 16-29, band high)
# licence of the source repository: see meta.json
import os
import morph_kgc
from rdflib.graph import Graph
from rdflib import compare

def test_RMLTC0000():
    g = Graph()
    g.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output.nq'))

    dict1 = {
    "students": []
    }
    data_dict = {"variable1":dict1}

    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl')
    config = f'[CONFIGURATION]\noutput_format=N-QUADS\n[DataSource]\nmappings={mapping_path}'
    g_morph = morph_kgc.materialize(config,data_dict)

    assert compare.isomorphic(g, g_morph)
