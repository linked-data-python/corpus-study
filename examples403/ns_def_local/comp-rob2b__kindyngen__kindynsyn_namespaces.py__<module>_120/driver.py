"""Validation driver for comp-rob2b__kindyngen__kindynsyn_namespaces.py__<module>_120.

NOT-EXPRESSIBLE (see meta.json). `translated.ldpy` is deliberately identical
to `original.py`: substituting `_NS = Namespace(...)` with `@prefix
rbdyn_coord: <...> .` breaks `RBDYN_COORD`'s attribute lookups outright
(`AttributeError: ... has no attribute '_NS'`), because `DefinedNamespace`
needs `_NS` as a runtime class attribute rather than a lexical binding. A
"green" verdict below only says the two files are the same program, not
that the construction was translated -- there is nothing to translate here
without breaking the class. See meta.json's translation_notes for the
reproduction.
"""
from rdfeval.harness import run_pair

# The region is a class *declaration*, not a callable: module-state
# comparison is the only oracle that fits. Neither side produces an
# rdflib.Graph or any harness-comparable value (a class object is not
# `_comparable`), so this call mainly confirms both sides import and define
# `RBDYN_COORD` without raising.
VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
