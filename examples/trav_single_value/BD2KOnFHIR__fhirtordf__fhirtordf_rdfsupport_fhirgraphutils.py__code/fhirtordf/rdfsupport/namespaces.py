# Context shim (see meta.json): subset of fhirtordf/rdfsupport/namespaces.py
# from BD2KOnFHIR/fhirtordf@05b23ba1df, so `from fhirtordf.rdfsupport.namespaces
# import FHIR` resolves outside the package (the real package is not
# installed/importable in this environment). Trimmed to the one namespace
# this region uses; identical bindings for both representations.
from fhirtordf.rdfsupport.dottednamespace import DottedNamespace

FHIR = DottedNamespace("http://hl7.org/fhir/")
