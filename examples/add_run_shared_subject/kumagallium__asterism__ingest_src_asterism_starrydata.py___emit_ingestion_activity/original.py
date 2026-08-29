# Extracted from kumagallium/asterism@f0977d4d3a : ingest/src/asterism/starrydata.py
# region: _emit_ingestion_activity (lines 476-496, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from datetime import UTC, datetime
from pathlib import Path
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, PROV, RDF, XSD
SCHEMA = Namespace("https://schema.org/")

def _emit_ingestion_activity(
    g: Graph,
    sd: Namespace,
    sdr: Namespace,
    csv_path: Path,
    run_id: str,
    started_at: datetime,
    software_agent_iri: str,
) -> URIRef:
    activity = sdr[f"ingestion/{run_id}"]
    g.add((activity, RDF.type, sd.IngestionActivity))
    g.add((activity, RDF.type, PROV.Activity))
    g.add(
        (activity, PROV.atTime, Literal(started_at.isoformat(), datatype=XSD.dateTime))
    )
    source = sdr[f"source/{csv_path.name}"]
    g.add((activity, PROV.used, source))
    g.add((source, RDF.type, PROV.Entity))
    g.add((source, SCHEMA.name, Literal(csv_path.name)))
    g.add((activity, PROV.wasAssociatedWith, URIRef(software_agent_iri)))
    return activity
