# Extracted from Display-Lab/scaffold@d368cfe17c : src/models/measure.py
# region: Measure.from_graph (lines 16-30, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph
from src.utils.namespace import FHIR

@classmethod
def from_graph(cls, graph: Graph) -> dict[str, "Measure"]:
    measures: dict[str, Measure] = {}

    for subject in graph.subjects(RDF.type, FHIR.Measure):
        identifier = str(graph.value(subject, FHIR.identifier))
        measures[identifier] = cls(
            identifier=identifier,
            name=str(graph.value(subject, FHIR.name)),
            title=str(graph.value(subject, FHIR.title)),
            measure_type=str(graph.value(subject, FHIR.type)),
            improvement_notation=str(graph.value(subject, FHIR.improvementNotation)),
        )

    return measures
