# Extracted from DataDrivenCPS/acquirium@e3bffb4bed : deployments/BENICIA/scripts/benicia_generator.py
# region: is_enumeration (lines 127-128, stratum trav_existence)
# licence of the source repository: see meta.json
import rdflib
from acquirium.internals.internals_namespaces import QUDT, QUDT_UNIT, S223

def is_enumeration(graph: rdflib.Graph, prop: rdflib.term.Identifier) -> bool:
    return any(graph.triples((prop, QUDT.hasEnumerationKind, None)))
