# Context shim (see meta.json): the one binding the region needs from its
# parent package, from MDD4REST/mdd4rest-annotator@c46839aa3d :
# server/src/rdflib2/plugins/parsers/pyRdfa/__init__.py, line 197 (verbatim):
#     ns_rdfa		= Namespace("http://www.w3.org/ns/rdfa#")
# so the region executes outside the package -- `from .. import ns_rdfa` is a
# relative import that needs a real parent package, which the harness (each
# side exec'd as a standalone script, see run_pair) does not give it.
# Identical binding for both representations.
#
# `ns_rdf` (rdflib's own RDF namespace, imported a few lines above this one
# in the region itself) needs no shim: `from rdflib import RDF as ns_rdf`
# resolves against the real, installed rdflib and stays in both files
# unchanged -- see translation_notes for why it still cannot use this same
# `from module import prefix:` construction.
from rdflib import Namespace

ns_rdfa = Namespace("http://www.w3.org/ns/rdfa#")
__namespaces__ = {"nsrdfa": ns_rdfa}
