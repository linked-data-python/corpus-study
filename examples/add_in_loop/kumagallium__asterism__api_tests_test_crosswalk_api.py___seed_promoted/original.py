# Extracted from kumagallium/asterism@f0977d4d3a : api/tests/test_crosswalk_api.py
# region: _seed_promoted (lines 75-99, stratum add_in_loop)
# licence of the source repository: see meta.json
import json
from pathlib import Path
import rdflib
from asterism import crosswalk_runtime, substrate
PRED = "https://kumagallium.github.io/asterism/x/ontology#comp"

def _seed_promoted(ds: rdflib.Dataset, registry_root: Path, dataset_id: str, rows) -> None:
    """A promoted dataset: rows in its key graph + control flag + a registry meta."""
    key = substrate.canonical_graph_iri(dataset_id)
    g = ds.graph(rdflib.URIRef(key))
    for entity, raw in rows:
        g.add((rdflib.URIRef(entity), rdflib.URIRef(PRED), rdflib.Literal(raw)))
    ds.update(
        f"INSERT DATA {{ GRAPH <{substrate.CONTROL_GRAPH_IRI}> {{ "
        f'<{key}> <{substrate.STATUS_PREDICATE}> "promoted" }} }}'
    )
    d = registry_root / dataset_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.json").write_text(
        json.dumps(
            {
                "id": dataset_id,
                "name": dataset_id,
                "created_at": "2026-06-11T00:00:00+00:00",
                "promoted": True,
                "status": "active",
                "canonical_graph": key,
            }
        ),
        encoding="utf-8",
    )
