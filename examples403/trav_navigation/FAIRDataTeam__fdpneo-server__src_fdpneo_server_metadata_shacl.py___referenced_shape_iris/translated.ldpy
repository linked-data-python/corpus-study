# Extracted from FAIRDataTeam/fdpneo-server@3e72e119ae : src/fdpneo_server/metadata/shacl.py
# region: _referenced_shape_iris (lines 216-234, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
from fdpneo_server.shared.namespaces import SH

def _referenced_shape_iris(graph: Graph) -> set[str]:
    """IRIs of shapes ``graph`` composes — to pull into the validation closure.

    Follows the SHACL constraint components that take a shape as their value:
    ``sh:node``, ``sh:qualifiedValueShape`` and ``sh:not`` (a single shape), and
    ``sh:and``/``sh:or``/``sh:xone`` (an RDF list of shapes). Only IRI references
    are returned — blank-node shapes are already inline in ``graph``.
    """
    refs: set[str] = set()
    for pred in (SH.node, SH.qualifiedValueShape, SH["not"]):
        refs.update(str(o) for o in graph.objects(None, pred) if isinstance(o, URIRef))
    for pred in (SH["and"], SH["or"], SH.xone):
        for list_node in graph.objects(None, pred):
            try:
                members = list(graph.items(list_node))
            except (ValueError, TypeError):  # malformed list — ignore
                continue
            refs.update(str(m) for m in members if isinstance(m, URIRef))
    return refs
