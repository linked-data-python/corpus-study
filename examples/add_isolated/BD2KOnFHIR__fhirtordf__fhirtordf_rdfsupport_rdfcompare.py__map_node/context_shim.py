# Context shim (see meta.json), for
# BD2KOnFHIR/fhirtordf@05b23ba1df9f322c148b7f20ebbd6d58cb92cefc.
#
# subj_pred_idx_to_uri is a module-level helper in the same source file,
# fhirtordf/rdfsupport/rdfcompare.py, immediately above map_node (lines
# 11-19 of that file) -- outside the extracted region's line range
# (22-36), so the region extraction did not capture it. Copied verbatim.
#
# FHIR replaces `from fhirtordf.rdfsupport.namespaces import FHIR`
# (fhirtordf/rdfsupport/namespaces.py): the real repository is not
# importable outside its own package, so a plain rdflib.Namespace stands
# in for the repo's DottedNamespace subclass -- map_node only ever does
# ordinary attribute access (FHIR.index), which both classes resolve
# identically to URIRef("http://hl7.org/fhir/index").
from typing import Optional

from rdflib import Namespace, URIRef

FHIR = Namespace("http://hl7.org/fhir/")


def subj_pred_idx_to_uri(s: URIRef, p: URIRef, idx: Optional[int] = None) -> URIRef:
    """Convert FHIR subject, predicate and entry index into a URI.  The
    resulting element can be substituted for the name of the target BNODE."""
    return URIRef(str(s) + '.' + str(p).rsplit('/', 1)[1] + ("_{}".format(idx) if idx is not None else ''))
