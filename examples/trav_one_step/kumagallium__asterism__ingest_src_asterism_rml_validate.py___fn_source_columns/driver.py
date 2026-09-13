"""Validation driver for kumagallium__asterism__ingest_src_asterism_rml_validate.py___fn_source_columns.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
from pathlib import Path
from rdflib import URIRef
from rdfeval.harness import run_pair, fixture_graph

_HERE = Path(__file__).resolve().parent
_FE1 = URIRef("http://example.org/fe1")
_FE3 = URIRef("http://example.org/fe3")

VERDICT = run_pair(
    __file__,
    entry='_fn_source_columns',
    calls=[
        lambda: ((fixture_graph(_HERE / "fixture.ttl"), _FE1), {}),
        lambda: ((fixture_graph(_HERE / "fixture.ttl"), _FE3), {}),
    ],
)
