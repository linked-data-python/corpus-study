# Extracted from battery-data-alliance/battery-data-format@7442a6fb9d : src/bdf/spec.py
# region: ColumnOntology.from_graph (lines 867-887, stratum trav_navigation)
# licence of the source repository: see meta.json
from typing import TYPE_CHECKING, Any, Literal
from rdflib.namespace import OWL, RDF, SKOS

@classmethod
def from_graph(cls, g: Any) -> "ColumnOntology":
    """Build ColumnOntology from an rdflib graph.

    Args:
        g: Parsed RDFlib graph object.

    Returns:
        New ColumnOntology instance.
    """
    quantities: dict[str, Quantity] = {}
    for subject in g.subjects(RDF.type, OWL.Class):
        q = Quantity.from_graph_subject(g, subject, SKOS, OWL)
        if q is not None:
            quantities[q.mr_name] = q

    version = next(
        (str(o) for s in g.subjects(RDF.type, OWL.Ontology) for o in g.objects(s, OWL.versionInfo)),
        "",
    )
    return cls(quantities, ontology_version=version)
