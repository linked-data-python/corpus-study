"""Validation driver for MKLab-ITI__prophet__rdflib_extras_infixowl.py__Property__set_domain.

The region is a property setter needing a live infixowl Property, so both
sides end with an identical demo harness; the mutated graph (``demo_graph``)
plus stdout is what gets compared.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # infixowl_ctx shim

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
