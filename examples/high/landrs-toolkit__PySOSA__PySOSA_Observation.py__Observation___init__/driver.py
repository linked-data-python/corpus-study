"""Validation driver for Observation.__init__.

The region is a constructor writing into the module-level ``obsgraph``, so
the driver compares module state: ``run_pair`` with ``entry=None`` pairs
every rdflib Graph in the two module namespaces and compares it by
isomorphism (the fresh ``BNode()`` per observation differs between the two
runs, which is exactly what isomorphism absorbs).

The two observations built by the demo harness at the end of both files
exercise the blank-node identity: two distinct subjects, one shared label.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)
