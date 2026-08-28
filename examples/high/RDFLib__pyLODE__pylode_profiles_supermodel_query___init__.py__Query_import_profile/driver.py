"""Validation driver: Query.import_profile is a method, and it is recursive
(`self.import_profile(...)`), so it cannot be called through the harness's
`entry=` path -- `self` would have to know which of the two modules it came
from.  Both files therefore end with the same small `__demo__` section that
binds the function onto the shim's DemoQuery, runs it from the root profile,
and leaves the result as module state: `imported_graph` (compared by
isomorphism) and a printed report of every quad with its graph name plus the
imported_profiles list (compared as stdout).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(__file__)
