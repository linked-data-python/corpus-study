"""Validation driver for MKLab-ITI__prophet__rdflib_extras_infixowl.py__Ontology___init__.

The region is a constructor that needs a live Ontology instance, so both
sides end with an identical demo harness; the graph it fills (``demo_graph``)
plus stdout is what gets compared.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # infixowl_ctx shim

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
