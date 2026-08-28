"""Validation driver for INCATools__kgcl-rdflib__kgcl_rdflib_kgcl.py__cli.

The region is a `click` Command, so it cannot be called through
run_pair(entry=...) with ordinary arguments.  Both sides therefore carry an
identical demo-harness section (see meta.json) that invokes the command the
way the console script does and parses back the Turtle it writes;
entry=None compares the resulting DEMO_GRAPH by isomorphism, plus stdout.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
