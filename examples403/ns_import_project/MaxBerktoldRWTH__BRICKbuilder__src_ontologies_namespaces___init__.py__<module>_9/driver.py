"""Validation driver for MaxBerktoldRWTH__BRICKbuilder__src_ontologies_namespaces___init__.py__<module>_9.

`demo()` (identical on both sides, appended after the region -- see
meta.json) dereferences one real term from each of the three re-exported
namespaces and returns their string forms: the only way to observe that a
prefix import resolves to the SAME IRI as the plain import it replaces,
since this region itself is a single import line with no graph operation
(rdf_ops=0) for the harness's default module-state comparison to see.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[((), {})],
)
