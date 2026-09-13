# Context shim (see meta.json): subset of lib/ktbs/namespace.py from
# ktbs/ktbs@4f9f50c770, so the region executes outside the package.
# Identical bindings for both representations.
from rdflib import Namespace

KTBS = Namespace("http://liris.cnrs.fr/silex/2009/ktbs#")
