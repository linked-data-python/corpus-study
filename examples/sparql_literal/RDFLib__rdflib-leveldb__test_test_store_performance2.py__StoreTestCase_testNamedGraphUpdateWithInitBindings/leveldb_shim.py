# Context shim (see meta.json): the two module-level imports of
# RDFLib/rdflib-leveldb@a0f3386c71 test/test_store_performance2.py that the
# region uses but does not define -- `import logging` (for
# `log = logging.getLogger(__name__)`) and `from rdflib import URIRef`.
# Identical bindings for both representations.
import logging
from rdflib import URIRef
