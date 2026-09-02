"""Validation driver for
JonAnderAsua__TFG-KG-RelacionesClientelares__procesSource_source_gate_cloud.py__TextToTriple_grafoaSortu.

`grafoaSortu` is a bare method (extracted without its enclosing
`TextToTriple` class): it reads `self.grafoa`, `self.balioztatu`,
`self.bilatuUria`, `self.getType` -- none visible in the extracted region.
`context_shim.TextToTripleStub` restores those bindings (see its docstring
and meta.json for what is verbatim vs. fixture-driven and why).

The fixture list below exercises everything the shared-subject fold and the
loop's guards depend on:
  - two annotations sharing one subject text ('Ada Lovelace' appears twice)
    so the `+{ }`/`.add()` triples really do land on ONE subject twice, not
    two -- the point of this stratum;
  - one of each filtered-out `annotationType` ('Sentence', 'Money', 'Date')
    that the `if` guard drops before `balioztatu` is even called;
  - one annotation `balioztatu` rejects (returns `False`) -- no triple;
  - one 'Location' annotation, since `getType` special-cases it to
    'https://schema.org/Place' rather than 'https://schema.org/Location'.
"""
from rdfeval.harness import run_pair

ANNOTATIONS = [
    {"annotationType": {"value": "Person"}, "annotationText": {"value": "Ada Lovelace"}},
    {"annotationType": {"value": "Person"}, "annotationText": {"value": "Ada Lovelace"}},
    {"annotationType": {"value": "Sentence"}, "annotationText": {"value": "A sentence, skipped before balioztatu"}},
    {"annotationType": {"value": "Money"}, "annotationText": {"value": "100 EUR"}},
    {"annotationType": {"value": "Date"}, "annotationText": {"value": "2024-01-01"}},
    {"annotationType": {"value": "Organization"}, "annotationText": {"value": "Rejected Org"}},
    {"annotationType": {"value": "Location"}, "annotationText": {"value": "Bilbao"}},
]

VALIDATIONS = {
    "Ada Lovelace": (True, "Person"),
    "Rejected Org": (False, ""),
    "Bilbao": (True, "Location"),
}

URIS = {
    "Ada Lovelace": "http://example.org/entity/Ada_Lovelace",
    "Bilbao": "http://example.org/entity/Bilbao",
}

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[((ANNOTATIONS, VALIDATIONS, URIS), {})],
)
