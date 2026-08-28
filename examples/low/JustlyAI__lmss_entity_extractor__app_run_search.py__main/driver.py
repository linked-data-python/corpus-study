"""Validation driver for JustlyAI__lmss_entity_extractor__app_run_search.py__main.

main() is a console entry point: no arguments, no return value, its graph is a
local.  The only observable is stdout, so the pair is compared in module-state
mode with the demo harness that both files carry (see meta.json).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
