# Context shim (see meta.json): the FHIR namespace that
# fhirtordf/rdfsupport/fhirgraphutils.py imports from
# fhirtordf.rdfsupport.namespaces, so the region executes without the
# fhirtordf package (not installed in this study's venv). Upstream, FHIR is
# a DottedNamespace("http://hl7.org/fhir/") (fhirtordf/rdfsupport/namespaces.py);
# DottedNamespace only adds dotted-attribute access (fhir:Patient.status),
# which this region does not use -- FHIR.value resolves identically as a
# plain rdflib Namespace. Identical bindings for both representations.
from rdflib import Namespace

FHIR = Namespace("http://hl7.org/fhir/")
