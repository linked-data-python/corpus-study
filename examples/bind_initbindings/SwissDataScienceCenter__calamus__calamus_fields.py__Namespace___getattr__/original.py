# Extracted from SwissDataScienceCenter/calamus@c59d6fe968 : calamus/fields.py
# region: Namespace.__getattr__ (lines 92-103, stratum bind_initbindings)
# licence of the source repository: see meta.json
# (added to make the region executable: `calamus` is not installed in the
# pinned study venv -- see context_shim.py for why a shim was used instead
# of installing it -- and `IRIReference` is a sibling class in the same
# source file, calamus/fields.py, dropped by the extraction because only
# the Namespace.__getattr__ qualname was selected; both restored from
# context_shim.py, see meta.json)
from context_shim import ONTOLOGY_QUERY, Proxy, normalize_type, normalize_value  # noqa: F401 (Proxy/normalize_* unused, see context_shim.py)
from context_shim import IRIReference

def __getattr__(self, name):
    reference = IRIReference(self, name)

    if self.ontology:
        from rdflib.term import URIRef

        p = URIRef(str(reference))
        qres = self.ontology.query(ONTOLOGY_QUERY, initBindings={"property": p})
        if not next(iter(qres), False):
            raise ValueError(f"Property {name} does not exist in namespace {self.namespace}")

    return reference
