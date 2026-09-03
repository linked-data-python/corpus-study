# Context shim (see meta.json): two of the Namespace objects the region
# imports from nanopub.namespaces (Nanopublication/nanopub-py@05022dc4bc),
# re-declared here with `__namespaces__` so ldpy's `from … import p:` can
# resolve them. `nanopub` is a real PyPI dependency and its `namespaces`
# module is imported directly (unshimmed) by original.py -- the gap is not
# executability, it is that an ordinary third-party module never exports
# `__namespaces__` (ldpy/012 points 21 and 15bis: a hand-written `.py`
# module can add `__namespaces__` by hand). Same fix as the ns_import_project
# sibling for this repository
# (Nanopublication__nanopub-py__tests_test_fdo_nanopub.py__test_add_fdo_profile),
# which shims HDL/FDOF/NPX from the same real module; this pair only needs
# FDOF/FDOC, so its own shim is scoped to those two. Identical bindings for
# both representations; values transcribed verbatim from
# nanopub/namespaces.py at the pinned commit (confirmed against the
# installed `nanopub` package: matches).
from rdflib import Namespace

FDOF = Namespace("https://w3id.org/fdof/ontology#")
FDOC = Namespace("https://w3id.org/fdoc/o/terms/")

__namespaces__ = {"fdof": FDOF, "fdoc": FDOC}
