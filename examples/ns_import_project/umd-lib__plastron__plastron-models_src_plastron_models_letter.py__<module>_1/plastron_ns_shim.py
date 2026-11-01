# Context shim (see meta.json): `plastron.namespaces` (umd-lib/plastron@4a7f08cc19,
# installed as plastron-utils 4.8.3) defines the namespaces as plain rdflib
# `Namespace` module attributes and has no `__namespaces__` registry, which
# `from module import p:` reads at run time. This shim re-exports the REAL
# objects of the package and adds the registry; nothing is re-defined.
# Only the translated side imports it.
from plastron.namespaces import (
    bibo, dc, dcmitype, dcterms, edm, geo, ore, owl, pcdm, rel, schema, skos, umd,
)

__namespaces__ = {
    "bibo": bibo, "dc": dc, "dcmitype": dcmitype, "dcterms": dcterms, "edm": edm,
    "geo": geo, "ore": ore, "owl": owl, "pcdm": pcdm, "rel": rel,
    "schema": schema, "skos": skos, "umd": umd,
}
