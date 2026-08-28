# Extracted from Informasjonsforvaltning/concepttordf@b06016d2ff : src/concepttordf/concept.py
# region: Concept._add_modified_to_bs_graph (lines 789-799, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
from .betydningsbeskrivelse import Betydningsbeskrivelse, RelationToSource
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
