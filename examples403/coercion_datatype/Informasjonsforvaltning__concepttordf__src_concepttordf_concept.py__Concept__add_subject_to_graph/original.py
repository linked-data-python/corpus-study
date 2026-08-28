# Extracted from Informasjonsforvaltning/concepttordf@b06016d2ff : src/concepttordf/concept.py
# region: Concept._add_subject_to_graph (lines 509-518, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, URIRef
DCT = Namespace("http://purl.org/dc/terms/")

def _add_subject_to_graph(self: Concept) -> None:
    if getattr(self, "subject", None):
        for key in self.subject:
            self._g.add(
                (
                    URIRef(self.identifier),
                    DCT.subject,
                    Literal(self.subject[key], lang=key),
                )
            )
