"""Validation driver for SoftwareHeritage__swh-indexer__swh_indexer_metadata_mapping_github.py__GitHubMapping_extra_translation.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
VERDICT = run_pair(
    __file__,
    entry='extra_translation',
    calls=[]  # TODO: [(args, kwargs), ...] fixtures,
)
