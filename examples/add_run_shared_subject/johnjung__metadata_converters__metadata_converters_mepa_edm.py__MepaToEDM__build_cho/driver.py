"""Validation driver for johnjung__metadata_converters__metadata_converters_mepa_edm.py__MepaToEDM__build_cho.

The region is one statement, run at module level, that adds a dcterms:hasPart
triple to `self.graph`. context_shim.py provides `self` (a MepaToEDM whose
graph already holds the work's title, another hasPart and the recto's
title): both modules are executed and the module-level values -- `self`, and
with it its graph -- are compared.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
