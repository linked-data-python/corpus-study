# Extracted from cognitedata/neat@4042d3e96d : cognite/neat/_v0/core/_data_model/exporters/_data_model2semantic_model.py
# region: OWLClass.title_triples (lines 202-213, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import DCTERMS, OWL, RDF, RDFS, XSD, BNode, Graph, Literal, Namespace, URIRef
from cognite.neat._v0.core._utils.rdf_ import remove_namespace_from_uri

@property
def title_triples(self) -> list[tuple]:
    if self.label:
        return [
            (
                self.id_,
                DCTERMS.title,
                Literal(f"{remove_namespace_from_uri(self.id_)} - {self.label}"),
            )
        ]
    else:
        return []
