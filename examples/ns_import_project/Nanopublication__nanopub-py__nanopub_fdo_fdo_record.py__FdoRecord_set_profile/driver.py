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

Two more calls (repair audit, 2026-10-31) take the shape of the repository's
own callers, which never pass `use_fdof`: `FdoRecord.__init__` calls
`self.set_profile(str(o))` (fdo_record.py:34) and
`self.set_profile(profile_uri)` (fdo_record.py:59, 69 -- "override if given
explicitly").  The default value of `use_fdof` is thus what decides the
predicate on every real path, and a mutated default (`= True`) stayed green
while every call passed it explicitly.  The fourth call relies on the
default with a `str`; the fifth also relies on it, on a `tuples` already
holding both predicates, so the overwrite of one key -- and only that one --
is compared.
"""
from types import SimpleNamespace
from rdflib import URIRef
from rdfeval.harness import run_pair


def _case(uri, use_fdof):
    return ((SimpleNamespace(tuples={}), uri), {"use_fdof": use_fdof})


def _default_case(uri, tuples):
    """As the repository calls it: no `use_fdof`, the default decides."""
    return ((SimpleNamespace(tuples=dict(tuples)), uri), {})


_EARLIER = {
    URIRef("http://purl.org/dc/terms/conformsTo"): URIRef("https://example.org/old"),
    URIRef("https://w3id.org/fdoc/o/terms/hasFdoProfile"): URIRef("https://example.org/old"),
}


VERDICT = run_pair(
    __file__,
    entry='set_profile',
    calls=[
        lambda: _case(URIRef("https://hdl.handle.net/21.T11966/UUID-PROFILE"), False),
        lambda: _case(URIRef("https://hdl.handle.net/21.T11966/UUID-PROFILE"), True),
        lambda: _case("https://hdl.handle.net/21.T11966/as-string", False),
        lambda: _default_case("https://hdl.handle.net/21.T11966/from-assertion", {}),
        lambda: _default_case(URIRef("https://hdl.handle.net/21.T11966/explicit"), _EARLIER),
    ],
)
