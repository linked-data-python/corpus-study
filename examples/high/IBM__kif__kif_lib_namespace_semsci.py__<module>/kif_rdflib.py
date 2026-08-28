# Context shim (see meta.json): kif_lib/rdflib.py (IBM/kif@4ce99d0d9b) is a
# thin re-export module over rdflib; only the three names this region imports
# are kept here, with the same provenance.
# Identical for both representations.
from rdflib import URIRef
from rdflib.namespace import DefinedNamespace, Namespace

__all__ = ('DefinedNamespace', 'Namespace', 'URIRef')
