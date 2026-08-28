# Extracted from bloodbee/jrt@2c5b072bcb : jrt/builder.py
# region: GraphBuilder.build (lines 47-63, stratum add_isolated)
# licence of the source repository: see meta.json
import warnings
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, FOAF, OWL, RDF, RDFS, SKOS, XSD

def build(self) -> Graph:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message=r".*is not defined in namespace XSD",
            category=UserWarning,
        )
        self._bind_namespaces()
        root_subject = self._materialize(self.data)
        if root_subject is not None:
            self.graph.add((root_subject, RDF.type, OWL.Thing))

        # Add external ontologies if provided
        if self.ontologies:
            for onto in self.ontologies:
                self.graph += onto.graph
    return self.graph
