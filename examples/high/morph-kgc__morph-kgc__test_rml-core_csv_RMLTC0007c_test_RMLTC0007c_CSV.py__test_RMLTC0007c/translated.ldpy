# Extracted from morph-kgc/morph-kgc@a2122e88bb : test/rml-core/csv/RMLTC0007c/test_RMLTC0007c_CSV.py
# region: test_RMLTC0007c (lines 16-24, band high)
# licence of the source repository: see meta.json
import os
import morph_kgc
from rdflib.graph import Graph
from rdflib import compare

def test_RMLTC0007c():
    g = Graph()
    g.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output.nq'))

    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl')
    config = f'[CONFIGURATION]\noutput_format=N-QUADS\n[DataSource]\nmappings={mapping_path}'
    g_morph = morph_kgc.materialize(config)

    assert compare.isomorphic(g, g_morph)
