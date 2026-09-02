"""Validation driver for
SoftwareHeritage__swh-indexer__swh_indexer_metadata_mapping_maven.py__<module>_12.

`demo()` (identical on both sides, appended after the region -- see
meta.json) dereferences the one real term the module uses this namespace
for (SCHEMA.codeRepository) and returns its string form: the only way to
observe that a prefix import resolves to the SAME IRI as the plain import
it replaces, since this region itself is a single import line with no
graph operation (rdf_ops=0) for the harness's default module-state
comparison to see.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[((), {})],
)
