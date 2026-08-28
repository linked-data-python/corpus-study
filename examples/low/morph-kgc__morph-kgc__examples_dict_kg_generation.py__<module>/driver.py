"""Validation driver for morph-kgc__morph-kgc__examples_dict_kg_generation.py__<module>.

Module-level region: both files are executed and every rdflib Graph in their
globals (here `g_rdflib`, the materialised knowledge graph) is compared by
isomorphism, together with the captured stdout (the triple dump the region
prints).  Needs ./config.ini and ./mapping.rml.ttl, so run from this directory.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__, entry=None, calls=None)
