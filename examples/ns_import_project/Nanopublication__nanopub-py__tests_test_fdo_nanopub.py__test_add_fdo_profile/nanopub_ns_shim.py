# Context shim (see meta.json): the three Namespace objects the region
# imports from nanopub.namespaces (Nanopublication/nanopub-py@05022dc4bc),
# re-declared here with `__namespaces__` so ldpy's `from … import p:` can
# resolve them. `nanopub` is a real PyPI dependency and its `namespaces`
# module is imported directly (unshimmed) by original.py -- the gap is not
# executability, it is that an ordinary third-party module never exports
# `__namespaces__` (design record ldpy/013 assumes both sides of such an
# import are ldpy modules; ldpy/012 points 21 and 15bis document exactly
# this gap, and its sanctioned fix: a hand-written `.py` module can add
# `__namespaces__` by hand). Identical bindings for both representations;
# values transcribed verbatim from nanopub/namespaces.py at the pinned
# commit.
from rdflib import Namespace

HDL = Namespace("https://hdl.handle.net/")
FDOF = Namespace("https://w3id.org/fdof/ontology#")
NPX = Namespace("http://purl.org/nanopub/x/")

__namespaces__ = {"hdl": HDL, "fdof": FDOF, "npx": NPX}
