"""Validation driver for MKLab-ITI__prophet__rdflib_extras_infixowl.py__GetIdentifiedClasses.

The region is a generator function, which the harness cannot compare
directly, so both sides end with an identical demo harness that exercises it
and leaves the outcome in module state (``demo_graph`` + stdout).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # infixowl_ctx shim

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
