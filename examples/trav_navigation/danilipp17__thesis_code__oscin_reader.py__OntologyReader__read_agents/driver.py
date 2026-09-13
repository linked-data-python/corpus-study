"""Validation driver for danilipp17__thesis_code__oscin_reader.py__OntologyReader__read_agents.

This region only READS a graph (it recovers a reasoning-pattern name, it does
not build one), so both original.py and translated.ldpy construct the same
small fixture graph inline and print the resulting `reasoning_pattern` to
stdout. entry=None runs both modules top to bottom and compares captured
stdout (plus any rdflib Graph left in globals).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
