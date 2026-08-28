# Extracted from citiususc/yatter@0b40dff623 : test/rml-star/YARRRMLTC-0028/test_yarrrmltc0028.py
# region: test_yarrrmltc0028 (lines 16-25, band high)
# licence of the source repository: see meta.json
import os
from ruamel.yaml import YAML
import yatter
from rdflib.graph import Graph
from rdflib import compare

def test_yarrrmltc0028():
    expected_mapping = Graph()
    expected_mapping.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl'), format="ttl")

    translated_mapping = Graph()
    yaml = YAML(typ='safe', pure=True)
    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yml')
    translated_mapping.parse(data=yatter.translate(yaml.load(open(mapping_path))), format="ttl")

    assert compare.isomorphic(expected_mapping, translated_mapping)
