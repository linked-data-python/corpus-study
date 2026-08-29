# Extracted from Congruentsys/yurtle-rdflib@8bbb378f5a : src/yurtle_rdflib/serializer.py
# region: YurtleRDFlibSerializer._filter_provenance_triples (lines 117-143, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from .namespaces import BEING, PM, PROVENANCE, YURTLE

def _filter_provenance_triples(self) -> Graph:
    """
    Create a copy of the graph without provenance triples.

    Provenance triples (definedIn) are used internally for tracking
    source files but should not be serialized back to Yurtle files.

    Returns:
        New Graph with provenance triples removed
    """
    filtered = Graph()

    # Copy namespace bindings
    for prefix, namespace in self.store.namespaces():
        filtered.bind(prefix, namespace)

    # Copy all triples except provenance
    for s, p, o in self.store:
        # Skip definedIn provenance triples
        if p == PROVENANCE.definedIn:
            continue
        # Skip file:// URIs in object position (also provenance)
        if isinstance(o, URIRef) and str(o).startswith("file://"):
            continue
        filtered.add((s, p, o))

    return filtered
