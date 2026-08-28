"""Validation driver for cognitedata__neat__…__raw.py__<module>.

A module-level region: importing it defines the RAWExtractor class and
nothing else, so both sides end with an identical demo harness that runs the
extractor over a canned RAW table; the harness then compares module state
(``demo_graph`` + stdout).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # neat_ctx shim

from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
