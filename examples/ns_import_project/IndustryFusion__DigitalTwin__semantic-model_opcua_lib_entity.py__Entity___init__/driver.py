"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_lib_entity.py__Entity___init__.

`demo(namespace_prefix, basens, opcuans)` (identical on both sides, appended
after the extracted region -- see meta.json) builds a plain `self`, calls
`__init__`, and returns the comparable results (not `self` itself -- a
plain object has no __eq__ and always compares unequal by identity, same
failure mode as the acdh-oeaw/vocabseditor sibling of this stratum).

This region is NOT-EXPRESSIBLE in ldpy's island syntax (see meta.json), so
original.py and translated.ldpy carry the identical body; the driver still
proves nothing was broken while restoring the region's executability.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        (("https://example.org/opcua/", "https://example.org/base/", "https://example.org/opcua-ns/"), {}),
    ],
)
