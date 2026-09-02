# Context shim (see meta.json): the three Namespace objects from
# prez/reference_data/prez_ns.py, RDFLib/prez@421ee0a9fee, so the region
# executes outside its package (`prez` is not published on PyPI -- checked
# directly, `pip index versions prez` finds no distribution -- so the real
# dotted path `prez.reference_data.prez_ns` does not resolve for a single
# extracted file) AND so ldpy's `from … import p:` can resolve them (the
# real module, an ordinary Python file, does not export `__namespaces__`).
# Identical bindings for both representations; values transcribed verbatim.
from rdflib import Namespace

REG = Namespace("http://purl.org/linked-data/registry#")
EP = Namespace("https://prez.dev/endpoint/")
TERN = Namespace("https://w3id.org/tern/ontologies/tern/")

__namespaces__ = {"reg": REG, "ep": EP, "tern": TERN}
