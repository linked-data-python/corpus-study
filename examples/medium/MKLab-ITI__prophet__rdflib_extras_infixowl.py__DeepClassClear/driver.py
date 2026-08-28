"""Validation driver: DeepClassClear prunes the graph reached through
Individual.factoryGraph -- a module-level attribute shared by the two runs,
which a driver fixture cannot set up (the harness builds both fixtures before
calling either side).  Both files therefore end with an identical demo harness
(see meta.json) replaying the region's own docstring scenario; the harness
compares the resulting demo_graph by isomorphism plus the printed trace.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)
