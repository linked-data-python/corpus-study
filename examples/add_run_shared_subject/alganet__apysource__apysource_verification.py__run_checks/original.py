# Extracted from alganet/apysource@f800ec97c1 : apysource/verification.py
# region: run_checks (lines 418-425, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from datetime import datetime, timezone
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, RDF, XSD
from apysource.namespaces import PROV, SV

if emit_provenance and prov_graph is not None:
    from apysource.namespaces import bind_prefixes
    bind_prefixes(prov_graph)
    activity = BNode()
    now = datetime.now(timezone.utc)
    prov_graph.add((activity, RDF.type, SV.VerificationActivity))
    prov_graph.add((activity, PROV.startedAtTime,
                    Literal(now.isoformat(), datatype=XSD.dateTime)))
