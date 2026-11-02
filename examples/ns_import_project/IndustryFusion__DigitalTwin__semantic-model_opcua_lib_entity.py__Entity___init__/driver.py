"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_lib_entity.py__Entity___init__.

`demo(namespace_prefix, basens, opcuans)` (identical on both sides, appended
after the extracted region -- see meta.json) builds a plain `self`, calls
`__init__`, and returns the comparable results (not `self` itself -- a
plain object has no __eq__ and always compares unequal by identity, same
failure mode as the acdh-oeaw/vocabseditor sibling of this stratum).

`entity_namespace` is built by `@prefix ... as ENTITY_NS` in the translation
and stored on `self`: the demo also subscripts it, as the sibling method
`Entity.set_attribute` does, and compares its type and the namespace bindings
of the graph `self.e` (the original's `bind` calls must survive).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        (("https://example.org/opcua/", "https://example.org/base/", "https://example.org/opcua-ns/"), {}),
        # another prefix, without a trailing slash: the IRI is the plain
        # concatenation `{namespace_prefix}entity/`, not a resolved one.
        (("urn:ex:opcua#", "https://example.org/base/", "https://example.org/opcua-ns/"), {}),
    ],
)
