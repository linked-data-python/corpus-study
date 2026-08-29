# Extracted from kumagallium/asterism@f0977d4d3a : api/tests/test_orphan_reclaim_api.py
# region: _has_pending_drop (lines 87-93, stratum trav_existence)
# licence of the source repository: see meta.json
import rdflib
from asterism import substrate

def _has_pending_drop(ds: rdflib.Dataset, graph_iri: str) -> bool:
    control = ds.graph(rdflib.URIRef(substrate.CONTROL_GRAPH_IRI))
    return any(
        control.triples(
            (rdflib.URIRef(graph_iri), rdflib.URIRef(substrate.PENDING_DROP_PREDICATE), None)
        )
    )
