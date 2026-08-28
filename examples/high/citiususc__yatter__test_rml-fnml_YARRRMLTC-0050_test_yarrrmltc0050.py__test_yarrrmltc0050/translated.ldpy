# Extracted from citiususc/yatter@0b40dff623 : test/rml-fnml/YARRRMLTC-0050/test_yarrrmltc0050.py
# region: test_yarrrmltc0050 (lines 16-25, band high)
# licence of the source repository: see meta.json
import os
from ruamel.yaml import YAML
import yatter
from rdflib.graph import Graph
from rdflib import compare

def test_yarrrmltc0050():
    expected_mapping = Graph()
    expected_mapping.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl'), format="ttl")

    translated_mapping = Graph()
    yaml = YAML(typ='safe', pure=True)
    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yml')
    translated_mapping.parse(data=yatter.translate(yaml.load(open(mapping_path))), format="ttl")

    assert compare.isomorphic(expected_mapping, translated_mapping)


# --- demo harness (not part of the extracted region; added IDENTICALLY to
# original.py and translated.ldpy so the driver has an observable) ----------
# The region is a pytest test that returns nothing, so run_pair(entry=...)
# would have nothing to compare: call it here (its own assertion still fires)
# and expose the two graphs it builds internally as module globals.
test_yarrrmltc0050()

DEMO_EXPECTED = Graph()
DEMO_EXPECTED.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.ttl'), format="ttl")
DEMO_TRANSLATED = Graph()
DEMO_TRANSLATED.parse(data=yatter.translate(YAML(typ='safe', pure=True).load(
    open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yml')))), format="ttl")
print(len(DEMO_EXPECTED), len(DEMO_TRANSLATED),
      compare.isomorphic(DEMO_EXPECTED, DEMO_TRANSLATED))
