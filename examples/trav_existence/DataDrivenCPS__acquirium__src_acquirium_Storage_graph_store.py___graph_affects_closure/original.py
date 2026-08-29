# Extracted from DataDrivenCPS/acquirium@e3bffb4bed : src/acquirium/Storage/graph_store.py
# region: _graph_affects_closure (lines 72-76, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Dataset, Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD, OWL, NamespaceManager

def _graph_affects_closure(graph: Graph) -> bool:
    """Return True if *graph* can change owl:imports-driven closure."""
    return any(graph.triples((None, OWL.imports, None))) or any(
        graph.triples((None, RDF.type, OWL.Ontology))
    )
