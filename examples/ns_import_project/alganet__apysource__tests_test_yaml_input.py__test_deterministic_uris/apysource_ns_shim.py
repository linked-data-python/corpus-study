# Context shim (see meta.json): `apysource.namespaces` (alganet/apysource@f800ec97c1,
# installed as apysource 0.10.0) defines SV, OA, SCHEMA as rdflib Namespaces but
# does not export a `__namespaces__` registry, which `from module import p:`
# reads at run time. This shim re-exports the REAL objects of the package and
# adds the registry; nothing is re-defined. Only the translated side imports it.
from apysource.namespaces import OA, SCHEMA, SV

__namespaces__ = {"oa": OA, "schema": SCHEMA, "sv": SV}
