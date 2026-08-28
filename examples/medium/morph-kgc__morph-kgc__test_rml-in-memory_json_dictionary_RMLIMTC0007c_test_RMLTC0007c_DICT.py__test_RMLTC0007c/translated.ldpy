# Extracted from morph-kgc/morph-kgc@a2122e88bb : test/rml-in-memory/json_dictionary/RMLIMTC0007c/test_RMLTC0007c_DICT.py
# region: test_RMLTC0007c (lines 16-33, band medium)
# licence of the source repository: see meta.json
import os
import morph_kgc
from rdflib.graph import Graph
from rdflib import compare

def test_RMLTC0007c():
    g = Graph()
    g.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output.nq'))

    dict1 = {
    "students": [{
        "ID": 10,
        "FirstName":"Venus",
        "LastName":"Williams"
    }]
    }
    data_dict = {"variable1":dict1}

    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl')
    config = f'[CONFIGURATION]\noutput_format=N-QUADS\n[DataSource]\nmappings={mapping_path}'
    g_morph = morph_kgc.materialize(config,data_dict)

    assert compare.isomorphic(g, g_morph)
