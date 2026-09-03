"""Validation driver for Nanopublication__nanopub-py__nanopub_fdo_fdo_record.py__FdoRecord_set_profile.

`set_profile` is a method body lifted out of `FdoRecord`: `self` is
duck-typed (the body only ever touches `self.tuples`), so it is called
directly with a `types.SimpleNamespace(tuples={})` standing in for a bare
instance. `SimpleNamespace` compares equal by `__dict__`, so the mutated
`self.tuples` dict IS the oracle: which predicate ends up holding `uri`
(`fdoc:hasFdoProfile` vs `dcterms:conformsTo`) is exactly what `use_fdof`
picks, and `run_pair` compares each call's mutated first argument (`args_o`
vs `args_t`) automatically. Two cases exercise both branches of that
choice; a third checks that a bare `str` `uri` still becomes a `URIRef` in
the stored value, matching `URIRef(uri)` in both branches.
"""
from types import SimpleNamespace
from rdflib import URIRef
from rdfeval.harness import run_pair


def _case(uri, use_fdof):
    return ((SimpleNamespace(tuples={}), uri), {"use_fdof": use_fdof})


VERDICT = run_pair(
    __file__,
    entry='set_profile',
    calls=[
        lambda: _case(URIRef("https://hdl.handle.net/21.T11966/UUID-PROFILE"), False),
        lambda: _case(URIRef("https://hdl.handle.net/21.T11966/UUID-PROFILE"), True),
        lambda: _case("https://hdl.handle.net/21.T11966/as-string", False),
    ],
)
