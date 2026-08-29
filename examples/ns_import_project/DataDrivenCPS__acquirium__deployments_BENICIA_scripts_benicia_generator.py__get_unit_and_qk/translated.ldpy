# Extracted from DataDrivenCPS/acquirium@e3bffb4bed : deployments/BENICIA/scripts/benicia_generator.py
# region: get_unit_and_qk (lines 107-115, stratum ns_import_project)
# licence of the source repository: see meta.json
from typing import Optional
import rdflib
from acquirium.internals.internals_namespaces import QUDT, QUDT_UNIT, S223

def get_unit_and_qk(
    graph: rdflib.Graph, prop: rdflib.term.Identifier
) -> tuple[Optional[str], Optional[str]]:
    unit_uri = next((str(u) for _, _, u in graph.triples((prop, QUDT.hasUnit, None))), None)
    qk = next(
        (str(q).split("/")[-1] for _, _, q in graph.triples((prop, QUDT.hasQuantityKind, None))),
        None,
    )
    return unit_uri, qk
