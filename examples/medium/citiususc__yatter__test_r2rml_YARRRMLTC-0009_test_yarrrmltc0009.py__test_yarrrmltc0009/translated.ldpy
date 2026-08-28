# Extracted from citiususc/yatter@0b40dff623 : test/r2rml/YARRRMLTC-0009/test_yarrrmltc0009.py
# region: test_yarrrmltc0009 (lines 17-32, band medium)
# licence of the source repository: see meta.json
import os
from ruamel.yaml import YAML
import yatter
from rdflib.graph import Graph
from rdflib import compare
R2RML_URI = 'http://www.w3.org/ns/r2rml#'

def test_yarrrmltc0009():
    expected_mapping = Graph()
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl'), 'r') as file:
        expected_mapping_string = file.read()
    expected_mapping.parse(data=expected_mapping_string, format="ttl")

    translated_mapping = Graph()
    yaml = YAML(typ='safe', pure=True)
    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yml')
    translated_mapping_string = yatter.translate(yaml.load(open(mapping_path)), mapping_format=R2RML_URI)
    translated_mapping.parse(data=translated_mapping_string, format="ttl")

    if compare.isomorphic(expected_mapping, translated_mapping):
        assert expected_mapping_string == translated_mapping_string
    else:
        assert False
