# Extracted from Informasjonsforvaltning/concepttordf@b06016d2ff : src/concepttordf/concept.py
# region: Concept._add_modified_to_bs_graph (lines 789-799, stratum coercion_datatype)
# licence of the source repository: see meta.json
from __future__ import annotations
from types import SimpleNamespace
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
from context_shim import Betydningsbeskrivelse, RelationToSource  # context shim, see meta.json
DCT = Namespace("http://purl.org/dc/terms/")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

def _add_modified_to_bs_graph(
    self: Concept, betydningsbeskrivelse: Betydningsbeskrivelse, bsnode: BNode
) -> None:
    if getattr(betydningsbeskrivelse, "modified", None):
        self._g.add(
            (
                bsnode,
                DCT.modified,
                Literal(betydningsbeskrivelse.modified, datatype=XSD.date),
            )
        )


# Demo harness (identical on both sides, see meta.json): `self: Concept` is a
# bound-method extraction -- Concept is the enclosing class, defined outside
# the extracted region, and the region only reaches through `self._g`. `self`
# and `betydningsbeskrivelse` stand in as plain SimpleNamespace objects
# exposing exactly the attributes the region reads (`_g`, `.modified`):
# neither Concept nor Betydningsbeskrivelse could be instantiated directly
# anyway (Betydningsbeskrivelse is an ABC with an abstract __init__). demo()
# calls the extracted method and returns the graph it wrote into, not `self`
# (comparing the stub instance itself would need an __eq__ for no benefit,
# since only the graph is the observable effect).
def demo(modified):
    self = SimpleNamespace(_g=Graph())
    betydningsbeskrivelse = SimpleNamespace(modified=modified)
    bsnode = BNode()
    _add_modified_to_bs_graph(self, betydningsbeskrivelse, bsnode)
    return self._g
