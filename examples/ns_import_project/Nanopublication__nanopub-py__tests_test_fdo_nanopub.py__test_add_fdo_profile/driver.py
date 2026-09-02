"""Validation driver for Nanopublication__nanopub-py__tests_test_fdo_nanopub.py__test_add_fdo_profile.

`test_add_fdo_profile` is called directly (bypassing pytest's own
parametrize collection, per convention -- see the sibling `trav_existence`
example in AGENT_BATCH's precedent) with the same two `fdo_profile` values
the real `@pytest.mark.parametrize` decorator lists: the bare handle
string, and its `hdl:` URIRef form. The region's own `assert (...) in
fdo.pubinfo`-style checks (now translated to `assert bool(m{ ... })`) ARE
the oracle: each side executes them for real against the RDF built by
unmodified project code (FdoNanopub, add_fdo_profile), and a wrong
translation raises AssertionError, which run_pair reports as an error.
"""
from rdflib import URIRef
from rdfeval.harness import run_pair

FAKE_HANDLE = "21.T11966/test"

VERDICT = run_pair(
    __file__,
    entry='test_add_fdo_profile',
    calls=[
        ((FAKE_HANDLE,), {}),
        ((URIRef("https://hdl.handle.net/" + FAKE_HANDLE),), {}),
    ],
)
