# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/validate_bfo_ontology.py
# region: _label (lines 108-114, stratum trav_existence)
# licence of the source repository: see meta.json
from typing import Any

def _label(iri: Any, g: Graph) -> str:
    if not isinstance(iri, (URIRef, BNode)):
        return str(iri) if iri is not None else "?"
    lbl = g.value(iri, RDFS.label) if isinstance(iri, URIRef) else None
    if lbl:
        return str(lbl)
    return _short(iri, g)
