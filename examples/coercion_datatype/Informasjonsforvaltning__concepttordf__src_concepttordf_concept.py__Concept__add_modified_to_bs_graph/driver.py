"""Validation driver for Informasjonsforvaltning__concepttordf__src_concepttordf_concept.py__Concept__add_modified_to_bs_graph.

`_add_modified_to_bs_graph` is a method (`self` an explicit first parameter,
`self: Concept`), so both sides carry an identical `demo(modified)` harness
(see meta.json and original.py) that builds a SimpleNamespace `self`
exposing `._g` and a SimpleNamespace `betydningsbeskrivelse` exposing
`.modified`, calls the extracted method, and returns `self._g` -- comparing
that graph, not the stub instances (which would need an __eq__ for no
benefit; the graph is the only observable effect).

CALL_1 -- modified set to a real `datetime.date`: exercises the truthy
branch and the coercion_datatype site itself (Literal(date_obj,
datatype=XSD.date) in original.py vs the language's default coercion in
translated.ldpy -- see meta.json for why the two agree exactly for a
`datetime.date` value).

CALL_2 -- modified=None: the falsy branch of `if getattr(...)`, contributing
no triple at all (the zero-triples edge).
"""
from datetime import date

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        ((date(2023, 6, 15),), {}),
        ((None,), {}),
    ],
)
