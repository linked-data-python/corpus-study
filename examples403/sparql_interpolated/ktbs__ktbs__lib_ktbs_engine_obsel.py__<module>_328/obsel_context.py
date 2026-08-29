# Context shim (see meta.json): a minimal stand-in for `KTBS` and `RDF` from
# lib/ktbs/namespace.py in ktbs/ktbs@4f9f50c770, so the region executes
# outside the package. The real KTBS is an rdflib ClosedNamespace built by
# parsing the whole kTBS OWL vocabulary description; only the IRI base and
# the `hasTrace` property this region uses are reproduced here, as a plain
# Namespace with the same IRI (http://liris.cnrs.fr/silex/2009/ktbs#).
# Identical bindings for both representations.
from rdflib import RDF, Namespace

KTBS = Namespace("http://liris.cnrs.fr/silex/2009/ktbs#")
