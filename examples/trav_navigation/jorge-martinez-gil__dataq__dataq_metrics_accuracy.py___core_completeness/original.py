# Extracted from jorge-martinez-gil/dataq@0808bf5696 : dataq/metrics/accuracy.py
# region: _core_completeness (lines 71-93, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF, URIRef
from ..namespaces import DCAT, DCT, RDF_NS
DCT_PROPERTIES = [DCT.title, DCT.identifier, DCT.description]

def _core_completeness(graph: Graph, property_set: str) -> float:
    """Completeness term used *inside* the accuracy formula.

    Mirrors ``core_links`` in the original script, where the DCAT required set
    is ``[dcat:title, rdf:type]`` (intentionally different from the standalone
    completeness dimension).
    """
    if property_set == "dct":
        required = DCT_PROPERTIES
    else:
        required = [DCAT.title, RDF_NS.type]

    scores = []
    for subject_type in (DCAT.Catalog, DCAT.Dataset, DCAT.Distribution):
        for subject in graph.subjects(RDF.type, subject_type):
            present = set()
            for predicate, _ in graph.predicate_objects(subject):
                if predicate in required:
                    present.add(predicate)
            scores.append((len(present) / len(required)) * 100)
    if not scores:
        return 0.0
    return sum(scores) / len(scores)
