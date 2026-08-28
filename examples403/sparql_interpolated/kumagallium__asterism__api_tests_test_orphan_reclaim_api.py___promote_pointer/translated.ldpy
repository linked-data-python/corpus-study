# Extracted from kumagallium/asterism@f0977d4d3a : api/tests/test_orphan_reclaim_api.py
# region: _promote_pointer (lines 77-84, stratum sparql_interpolated)
# licence of the source repository: see meta.json
import rdflib
from asterism import substrate

def _promote_pointer(ds: rdflib.Dataset, dataset_id: str, live_iri: str) -> None:
    """Flag ``dataset_id`` promoted with ``liveGraph`` -> ``live_iri`` (referenced)."""
    key = substrate.canonical_graph_iri(dataset_id)
    ds.update(
        f"INSERT DATA {{ GRAPH <{substrate.CONTROL_GRAPH_IRI}> {{ "
        f'<{key}> <{substrate.STATUS_PREDICATE}> "{substrate.STATUS_PROMOTED}" ; '
        f"<{substrate.LIVE_GRAPH_PREDICATE}> <{live_iri}> }} }}"
    )
