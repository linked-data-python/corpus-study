# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/ontospecies_extension/operations/ontospecies_extension.py
# region: delete_triple (lines 603-622, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from context_shim import locked_graph, _is_abs_iri

def delete_triple(subject_iri: str, predicate_iri: str, object_value: str) -> str:
    """Remove one RDF triple matching the given subject, predicate, and object."""
    with locked_graph() as g:
        if not _is_abs_iri(subject_iri) or not _is_abs_iri(predicate_iri):
            return "subject_iri and predicate_iri must be absolute https IRIs"

        s = URIRef(subject_iri)
        p = URIRef(predicate_iri)

        # Determine if object is IRI or literal
        if _is_abs_iri(object_value):
            o = URIRef(object_value)
        else:
            o = Literal(object_value)

        if (s, p, o) in g:
            g.remove((s, p, o))
            return f"Removed triple ({s}, {p}, {o})"
        else:
            return f"No such triple found: ({s}, {p}, {o})"
