# Context shim (see meta.json): `pyrml` is not an installed dependency in
# this environment, so this stands in for the two pieces of
# anuzzolese/pyrml@d18fe2edfc the region needs but does not itself define.
# Identical on both sides.
#
# 1. pyrml/rml_vocab.py -- RR_NS/RML_NS are real rdflib Namespace objects
#    over the real R2RML/RML vocabulary IRIs, copied verbatim from that
#    file (only the two members this region uses are reproduced).
#
# 2. TripleMappings.__build (pyrml_core.py:1647), the other half of the
#    TripleMappings class this region's `from_rdf` belongs to. The real
#    method builds a full TripleMappings instance via LogicalSource.from_rdf,
#    SubjectMap.from_rdf and PredicateObjectMap.from_rdf -- machinery well
#    outside this region, and none of it reads anything from `g` that
#    `from_rdf` itself has not already read. The stand-in below returns the
#    selected triples-map subject `tm` itself, which is exactly the value
#    `from_rdf`'s own read/selection logic (the code under test) computes --
#    enough to observe which subjects the region selected, nothing about
#    what a real TripleMappings object would contain.
#
#    `__build` is assigned onto the class from OUTSIDE its body on purpose:
#    a `def __build(self, ...):` written INSIDE `class TripleMappings:`
#    would be name-mangled to `_TripleMappings__build` by Python, but
#    `from_rdf` (extracted on its own, no longer textually inside the real
#    class) calls the UNMANGLED `TripleMappings.__build(g, tm)` -- so the
#    stand-in must be reachable under that exact literal name.
from rdflib import Namespace

RR_NS = Namespace("http://www.w3.org/ns/r2rml#")
RML_NS = Namespace("http://semweb.mmlab.be/ns/rml#")


class rml_vocab:
    RR_NS = RR_NS
    RML_NS = RML_NS


class TermMap:
    """Stand-in for pyrml.pyrml_api.TermMap -- used only as a type hint here."""


class TripleMappings:
    """Stand-in for pyrml_core.py's TripleMappings; see module docstring."""


def _build(g, tm):
    return tm


TripleMappings.__build = staticmethod(_build)
