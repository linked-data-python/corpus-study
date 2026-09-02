# Context shim (see meta.json): the subset of the project's own
# pyshacl/consts.py needed by this region, from RDFLib/pySHACL@469cca7a22 :
#     RDF_PFX = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
#     RDFS_PFX = 'http://www.w3.org/2000/01/rdf-schema#'
#     SH_PFX = 'http://www.w3.org/ns/shacl#'
#     RDF = Namespace(RDF_PFX)
#     RDFS = Namespace(RDFS_PFX)
#     SH = Namespace(SH_PFX)
#     RDF_type = RDF.type
#     SH_property = SH.property
# `pyshacl.consts` is a plain rdflib-based Python module (not written in
# ldpy), so `from pyshacl.consts import rdfs:, sh:` cannot resolve prefixes
# from it directly -- the transpiler needs a module-level `__namespaces__`
# export. This shim reproduces the same project-owned bindings and adds
# that export; the two names that are already-derived terms rather than
# namespaces (RDF_type, SH_property) travel as ordinary Python names,
# identically on both sides.
from rdflib.namespace import Namespace

RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SH = Namespace("http://www.w3.org/ns/shacl#")

RDF_type = RDF.type
SH_property = SH.property

__namespaces__ = {"rdfs": RDFS, "sh": SH}
