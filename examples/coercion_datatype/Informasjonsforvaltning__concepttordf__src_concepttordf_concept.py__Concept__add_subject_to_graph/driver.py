"""Validation driver for Informasjonsforvaltning__concepttordf__src_concepttordf_concept.py__Concept__add_subject_to_graph.

`_add_subject_to_graph` is a method (`self` an explicit first parameter,
`self: Concept`), so both sides carry an identical `demo(identifier,
subject)` harness (see meta.json and original.py) that builds a
SimpleNamespace `self` exposing `._g`, `.identifier` and `.subject`, calls
the extracted method, and returns `self._g` -- comparing that graph, not the
stub instance (which would need an __eq__ for no benefit; the graph is the
only observable effect).

CALL_1 -- subject holds two language-tagged entries (en, nb): exercises the
truthy branch, the loop over dict keys, and the coercion_datatype site
itself, `Literal(self.subject[key], lang=key)` where `key` -- the language
tag -- is a runtime value, not a literal written in source (see meta.json
for why this puts it out of reach of the language's `"..."@lang` notation,
and how the region falls back to a passed-through `Literal(...)` call).

CALL_2 -- subject=None: the falsy branch of `if getattr(...)`, contributing
no triple at all (the zero-triples edge, matching the sibling region's
CALL_2).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        (("http://example.com/concepts/1",
          {"en": "Example subject", "nb": "Eksempel emne"}), {}),
        (("http://example.com/concepts/1", None), {}),
    ],
)
