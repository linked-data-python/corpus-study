"""Validation driver for BrickSchema__Brick__examples_air_quality_sensors_generate.py__<module>.

The region is a script: it builds `brick` and `g` at module level and prints
its query results, so entry=None compares both graphs by isomorphism and the
captured stdout without any harness code being added to either side.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
