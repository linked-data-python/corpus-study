# Context shim (see meta.json): subset of shapiro_model.py from
# mathiasrichter/shapiro@3954ef2148, so the region executes outside the
# package. Reproduces NodeShape.__init__ -> SemanticModelElement.__init__'s
# label computation (also an initBindings query) closely enough for
# get_nodeshapes' `shapes.sort(key=lambda s: s.label)` to behave the same,
# and ShaclProperty.SHAPE_QUERY, the query the region itself runs.
# Identical bindings for both representations.
from urllib.parse import urlparse

from rdflib import Graph, URIRef
from rdflib.plugins.sparql import prepareQuery

SHAPE_QUERY = prepareQuery(
    """
    PREFIX sh:<http://www.w3.org/ns/shacl#>
    SELECT DISTINCT ?shape
    WHERE
    {
        ?shape sh:property ?property .
    }
    """
)

DESCRIPTION_QUERY = prepareQuery(
    """
    PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?label
    WHERE
    {
        OPTIONAL { ?model rdfs:label ?label . }
    }
    """
)


def prune_iri(iri: str, name_only: bool = False) -> str:
    url = urlparse(iri)
    result = url.path.strip("/")
    result = result.split("/")[-1] if not url.fragment else url.fragment
    return result


class NodeShape:
    """Minimal stand-in for shapiro_model.NodeShape."""

    def __init__(self, iri: str, graph: Graph):
        self.iri = str(iri)
        self.graph = graph
        self.label = self._get_label()

    def _get_label(self) -> str:
        result = self.graph.query(
            DESCRIPTION_QUERY, initBindings={"model": URIRef(self.iri)}
        )
        for r in result:
            if r.label is not None:
                return str(r.label)
        return prune_iri(self.iri, True)

    def __eq__(self, other):
        return (
            isinstance(other, NodeShape)
            and self.iri == other.iri
            and self.label == other.label
        )

    def __repr__(self):
        return f"NodeShape({self.iri!r}, {self.label!r})"
